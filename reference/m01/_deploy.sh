#!/usr/bin/env bash
# M1 deploy: MinIO (raw manifests) + Postgres (own Helm chart) into `storage`.
set -euo pipefail
kubectl apply -f platform/k8s/storage/
kubectl -n storage rollout status deploy/minio --timeout=180s
kubectl -n storage wait --for=condition=complete job/minio-buckets --timeout=180s || true
helm upgrade --install postgres platform/charts/postgres -n storage \
  -f platform/helm-values/postgres.yaml --wait --timeout 5m
