import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Collect all lab RPC and ping timings")
    parser.add_argument("--same-zone", required=True)
    parser.add_argument("--different-region", required=True)
    args = parser.parse_args()
    output = Path("output")
    output.mkdir(exist_ok=True)
    results = {}
    for label, host, reps in (
        ("Local", "localhost", 1000),
        ("Same-Zone", args.same_zone, 1000),
        ("Different Region", args.different_region, 100),
    ):
        results[label] = {"host": host, "repetitions": reps, "methods": {}}
        for protocol in ("REST", "gRPC"):
            for method in ("add", "rawimage", "dotproduct", "jsonimage"):
                command = [
                    sys.executable,
                    f"{protocol.lower()}-client.py",
                    host,
                    method,
                    str(reps),
                ]
                result = subprocess.run(
                    command, capture_output=True, text=True, check=True, timeout=1800
                )
                print(f"{label} {protocol} {result.stdout.strip()}", flush=True)
                results[label]["methods"][f"{protocol} {method}"] = float(
                    re.search(r": ([0-9.]+) ms", result.stdout)[1]
                )
                (output / "results.json").write_text(
                    json.dumps(results, indent=2) + "\n"
                )
        ping = subprocess.run(
            ["ping", "-c", "20", "-i", "0.2", host],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        (output / f"ping-{label.lower().replace(' ', '-')}.txt").write_text(ping.stdout)
        results[label]["ping_ms"] = float(
            re.search(r"= [0-9.]+/([0-9.]+)/", ping.stdout)[1]
        )
        (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        print(f"{label} ping: {results[label]['ping_ms']} ms", flush=True)


if __name__ == "__main__":
    main()
