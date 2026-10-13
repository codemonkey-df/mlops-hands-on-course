#!/usr/bin/env bash
# Tag and push a local image to Harbor:  ./push.sh <local-image> <repo:tag>
set -euo pipefail
# PUSH name: Docker allows plain HTTP only for 127.0.0.0/8 (see `docker info`).
REGISTRY=127.0.0.1:8085
docker tag "$1" "$REGISTRY/mlops/$2"
docker push -q "$REGISTRY/mlops/$2"
