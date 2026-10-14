#!/usr/bin/env python3
import requests

from common import client_args, measure, payload


def main():
    args = client_args(5000)
    data, expected = payload(args.cmd)
    url = f"http://{args.host}:{args.port}/api/{args.cmd}"
    if args.cmd == "add":
        url += f"/{data['a']}/{data['b']}"
        kwargs = {}
    elif args.cmd == "rawimage":
        kwargs = {"data": data["img"], "headers": {"Content-Type": "image/jpeg"}}
    elif args.cmd == "jsonimage":
        kwargs = {"json": {"image": data["img"]}}
    else:
        kwargs = {"json": data}

    def call():
        # Each call opens a connection as required by the lab.
        response = requests.post(url, timeout=60, **kwargs)
        response.raise_for_status()
        return response.json()

    measure(args, call, expected)


if __name__ == "__main__":
    main()
