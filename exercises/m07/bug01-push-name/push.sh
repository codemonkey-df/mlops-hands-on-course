#!/usr/bin/env bash
# Tag and push a local image to Harbor:  ./push.sh <local-image> <repo:tag>
set -euo pipefail
# Harbor runs on the LXC
REGISTRY=YOUR_SERVER_IP:8085
docker tag "$1" "$REGISTRY/mlops/$2"
docker push -q "$REGISTRY/mlops/$2"
