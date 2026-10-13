#!/usr/bin/env bash
# M5 deploy: build + import the user-code image, install the Dagster chart,
# turn on the drift sensor.
set -euo pipefail
# The tag must match dagster-user-deployments.deployments[0].image.tag in the values.
TAG=0.1.0

docker build -f platform/images/dagster-code/Dockerfile -t "mlops/dagster-code:$TAG" .
k3d image import "mlops/dagster-code:$TAG" -c mlops
kubectl apply -f platform/k8s/dagster/
helm repo add dagster https://dagster-io.github.io/helm >/dev/null 2>&1 || true
helm upgrade --install dagster dagster/dagster --version 1.13.26 -n dagster \
  -f platform/helm-values/dagster.yaml --wait --timeout 10m
kubectl -n dagster exec deploy/dagster-dagster-webserver -c dagster -- \
  dagster sensor start drift_sensor -w /dagster-workspace/workspace.yaml -l churn || true
echo "UI: http://dagster.YOUR_SERVER_IP.nip.io:8080"
