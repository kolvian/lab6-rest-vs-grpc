#!/usr/bin/env python3
import argparse
import logging

from flask import Flask, jsonify, request

from common import decode_image, dot_product, image_size

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


@app.errorhandler(TypeError)
@app.errorhandler(ValueError)
def bad_request(error):
    return jsonify(error=str(error)), 400


def json_body():
    data = request.get_json()
    if not isinstance(data, dict):
        raise TypeError("body must be a JSON object")
    return data


@app.route(
    "/api/add/<int(signed=True):a>/<int(signed=True):b>", methods=["GET", "POST"]
)
def add(a, b):
    return jsonify(sum=a + b)


@app.post("/api/rawimage")
def rawimage():
    return jsonify(image_size(request.data))


@app.post("/api/dotproduct")
def dotproduct():
    data = json_body()
    return jsonify(dotproduct=dot_product(data.get("a"), data.get("b")))


@app.post("/api/jsonimage")
def jsonimage():
    return jsonify(image_size(decode_image(json_body().get("image"))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="REST server")
    parser.add_argument("-p", "--port", type=int, default=5000)
    app.run(host="0.0.0.0", port=parser.parse_args().port)
