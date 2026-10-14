#!/bin/bash
set -eux
apt-get update
apt-get install -y python3-venv python3-pip iputils-ping
mkdir -p /opt/lab6
python3 -m venv /opt/lab6/.venv
/opt/lab6/.venv/bin/pip install flask==3.1.3 pillow==12.3.0 requests==2.34.2 grpcio==1.84.0 grpcio-tools==1.84.0 protobuf==7.36.2
touch /opt/lab6/ready
