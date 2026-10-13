#!/usr/bin/env bash
# Build + push a release of the "hello" app.  ./release.sh <version>
# Prints the image reference the cluster must run (pull name).
set -euo pipefail
version="$1"
# Always deploy the newest build.
tag=latest
ctx=$(mktemp -d); trap 'rm -rf "$ctx"' EXIT
printf 'FROM busybox:1.37\nCMD ["echo", "hello %s"]\n' "$version" > "$ctx/Dockerfile"
docker build -q -t "127.0.0.1:8085/mlops/ex-hello:$tag" "$ctx" >/dev/null
docker push -q "127.0.0.1:8085/mlops/ex-hello:$tag" >/dev/null
echo "harbor.local:8085/mlops/ex-hello:$tag"
