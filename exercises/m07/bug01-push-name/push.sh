#!/usr/bin/env bash
# Tag and push a local image to Harbor:  ./push.sh <local-image> <repo:tag>
set -euo pipefail
# Harbor runs on the LXC
REGISTRY=192.168.1.202:8085
docker tag "$1" "$REGISTRY/mlops/$2"
docker push -q "$REGISTRY/mlops/$2"
