#!/usr/bin/env python3
import grpc

import lab6_pb2 as messages
import lab6_pb2_grpc as services
from common import client_args, measure, payload


def main():
    args = client_args(50051)
    data, expected = payload(args.cmd)
    types = {
        "add": ("Add", messages.addMsg),
        "rawimage": ("RawImage", messages.rawImageMsg),
        "dotproduct": ("DotProduct", messages.dotProductMsg),
        "jsonimage": ("JsonImage", messages.jsonImageMsg),
    }
    name, message_type = types[args.cmd]
    request = message_type(**data)
    with grpc.insecure_channel(f"{args.host}:{args.port}") as channel:
        grpc.channel_ready_future(channel).result(timeout=60)
        method = getattr(services.Lab6Stub(channel), name)

        def call():
            result = method(request, timeout=60)
            return {key: getattr(result, key) for key in expected}

        measure(args, call, expected)


if __name__ == "__main__":
    main()
