import argparse
import base64
import io
import math
import random
import time
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def dot_product(a, b):
    if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)):
        raise TypeError("a and b must be lists")
    if len(a) != len(b):
        raise ValueError("a and b must have equal lengths")
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in (*a, *b)):
        raise ValueError("vectors must contain finite numbers")
    result = sum(x * y for x, y in zip(a, b))
    if not math.isfinite(result):
        raise ValueError("dot product must be finite")
    return result


def image_size(data):
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ("JPEG", "PNG"):
                raise ValueError("image must be JPEG or PNG")
            return {"width": image.width, "height": image.height}
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("invalid image") from error


def decode_image(text):
    if not isinstance(text, str):
        raise TypeError("image must be a base64 string")
    return base64.b64decode(text, validate=True)


def client_args(port):
    parser = argparse.ArgumentParser(description="Measure RPC time in milliseconds")
    parser.add_argument("host")
    parser.add_argument(
        "cmd", type=str.lower, choices=["add", "rawimage", "dotproduct", "jsonimage"]
    )
    parser.add_argument("reps", type=int)
    parser.add_argument("-p", "--port", type=int, default=port)
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    if args.reps < 1:
        parser.error("reps must be positive")
    return args


def payload(cmd):
    if cmd == "add":
        return {"a": 5, "b": 10}, {"sum": 15}
    if cmd == "dotproduct":
        random.seed(6)
        a = [random.random() for _ in range(100)]
        b = [random.random() for _ in range(100)]
        return {"a": a, "b": b}, {"dotproduct": dot_product(a, b)}
    image = Path(__file__).with_name("Flatirons_Winter_Sunrise_edit_2.jpg").read_bytes()
    value = image if cmd == "rawimage" else base64.b64encode(image).decode("ascii")
    return {"img": value}, image_size(image)


def measure(args, call, expected):
    def check(result):
        for key, value in expected.items():
            if not math.isclose(float(result[key]), value, rel_tol=1e-6, abs_tol=1e-6):
                raise AssertionError(f"Incorrect response: {result}")

    check(call())
    start = time.perf_counter()
    for _ in range(args.reps):
        result = call()
        check(result)
        if args.debug:
            print(result)
    elapsed = (time.perf_counter() - start) * 1000 / args.reps
    print(f"{args.cmd}: {elapsed:.6f} ms per operation ({args.reps} reps)")
