import base64
import importlib.util
import math
from concurrent import futures
from pathlib import Path

import grpc

import lab6_pb2 as messages
import lab6_pb2_grpc as services
from common import dot_product, image_size


def load(name):
    spec = importlib.util.spec_from_file_location(name, f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    image = Path("Flatirons_Winter_Sunrise_edit_2.jpg").read_bytes()
    dimensions = image_size(image)
    encoded = base64.b64encode(image).decode("ascii")
    rest = load("rest-server").app.test_client()
    assert rest.post("/api/add/-5/10").json == {"sum": 5}
    for a, b in (([], []), ([1, 2], [3, 4]), ([0.25] * 101, [0.5] * 101)):
        assert rest.post("/api/dotproduct", json={"a": a, "b": b}).json == {
            "dotproduct": dot_product(a, b)
        }
    assert rest.post("/api/rawimage", data=image).json == dimensions
    assert rest.post("/api/jsonimage", json={"image": encoded}).json == dimensions
    for data in (
        {"a": [1], "b": []},
        {"a": [True], "b": [1]},
        {"a": ["x"], "b": [1]},
        {},
    ):
        assert rest.post("/api/dotproduct", json=data).status_code == 400
    assert rest.post("/api/jsonimage", json={"image": "!"}).status_code == 400
    assert rest.post("/api/rawimage", data=b"bad").status_code == 400
    assert rest.post("/api/dotproduct", json=[]).status_code == 400

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    services.add_Lab6Servicer_to_server(load("grpc-server").Lab6(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as channel:
            stub = services.Lab6Stub(channel)
            assert stub.Add(messages.addMsg(a=-5, b=10), timeout=5).sum == 5
            for a, b in (([], []), ([1, 2], [3, 4]), ([0.25] * 101, [0.5] * 101)):
                assert math.isclose(
                    stub.DotProduct(
                        messages.dotProductMsg(a=a, b=b), timeout=5
                    ).dotproduct,
                    dot_product(a, b),
                )
            for result in (
                stub.RawImage(messages.rawImageMsg(img=image), timeout=5),
                stub.JsonImage(messages.jsonImageMsg(img=encoded), timeout=5),
            ):
                assert {"width": result.width, "height": result.height} == dimensions
            for method, request in (
                (stub.DotProduct, messages.dotProductMsg(a=[1], b=[])),
                (stub.RawImage, messages.rawImageMsg(img=b"bad")),
                (stub.JsonImage, messages.jsonImageMsg(img="!")),
                (stub.Add, messages.addMsg(a=2**31 - 1, b=1)),
            ):
                try:
                    method(request, timeout=5)
                except grpc.RpcError as error:
                    assert error.code() == grpc.StatusCode.INVALID_ARGUMENT
                else:
                    raise AssertionError("Invalid request was accepted")
    finally:
        server.stop(0).wait()
    print("All REST and gRPC correctness checks passed.")


if __name__ == "__main__":
    main()
