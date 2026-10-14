#!/usr/bin/env python3
import argparse
from concurrent import futures

import grpc

import lab6_pb2 as messages
import lab6_pb2_grpc as services
from common import decode_image, dot_product, image_size


class Lab6(services.Lab6Servicer):
    def Add(self, request, context):
        total = request.a + request.b
        if not -(2**31) <= total < 2**31:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "sum exceeds int32 range")
        return messages.addReply(sum=total)

    def RawImage(self, request, context):
        try:
            return messages.imageReply(**image_size(request.img))
        except (TypeError, ValueError) as error:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))

    def DotProduct(self, request, context):
        try:
            value = dot_product(list(request.a), list(request.b))
            if abs(value) > 3.4028234663852886e38:
                raise ValueError("dot product exceeds float32 range")
            return messages.dotProductReply(dotproduct=value)
        except (TypeError, ValueError) as error:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))

    def JsonImage(self, request, context):
        try:
            return messages.imageReply(**image_size(decode_image(request.img)))
        except (TypeError, ValueError) as error:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gRPC server")
    parser.add_argument("-p", "--port", type=int, default=50051)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    services.add_Lab6Servicer_to_server(Lab6(), server)
    server.add_insecure_port(f"0.0.0.0:{parser.parse_args().port}")
    server.start()
    server.wait_for_termination()
