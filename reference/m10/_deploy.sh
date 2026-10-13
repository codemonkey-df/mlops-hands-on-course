#!/usr/bin/env bash
# M10 deploy: Prometheus stack + KEDA (Helm, once), rebuild mock-vllm so the
# image contains the DCGM sidecar module. Argo CD picks up chart/dashboard
# changes after you commit and push platform/.
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo add kedacore https://kedacore.github.io/charts >/dev/null 2>&1 || true
helm repo update >/dev/null

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --version 92.3.1 \
  --namespace observability --create-namespace \
  --values platform/helm-values/kube-prometheus-stack.yaml \
  --wait --timeout 10m

helm upgrade --install keda kedacore/keda \
  --version 2.21.0 \
  --namespace keda --create-namespace \
  --values platform/helm-values/keda.yaml \
  --wait --timeout 5m

# shellcheck disable=SC1091
source infra/compose/harbor/robots.env
printf '%s' "$HARBOR_CI_SECRET" | docker login 127.0.0.1:8085 -u "$HARBOR_CI_USER" --password-stdin >/dev/null
docker build -q -f platform/images/mock-vllm/Dockerfile -t 127.0.0.1:8085/mlops/mock-vllm:0.1.0 .
docker push -q 127.0.0.1:8085/mlops/mock-vllm:0.1.0

echo "stack ready:"
echo "  Grafana    http://grafana.192.168.1.202.nip.io:8080   (admin / lab)"
echo "  Prometheus http://prometheus.192.168.1.202.nip.io:8080"
echo "now: git add platform src tests && git commit -m 'm10: observability' && git push gitea main"
