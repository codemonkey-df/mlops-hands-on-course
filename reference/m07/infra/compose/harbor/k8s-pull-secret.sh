#!/usr/bin/env bash
# Create/refresh the "harbor-pull" imagePullSecret (pull-only robot) in the
# given namespaces and attach it to their default ServiceAccount, so pods
# pull from Harbor without listing imagePullSecrets in every manifest.
#   infra/compose/harbor/k8s-pull-secret.sh serving dagster
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source robots.env
for ns in "$@"; do
  kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  # The server MUST match the image prefix the pods use (pull name).
  kubectl -n "$ns" create secret docker-registry harbor-pull \
    --docker-server=harbor.local:8085 \
    --docker-username="$HARBOR_K8S_USER" --docker-password="$HARBOR_K8S_SECRET" \
    --dry-run=client -o yaml | kubectl apply -f - >/dev/null
  kubectl -n "$ns" patch serviceaccount default \
    -p '{"imagePullSecrets":[{"name":"harbor-pull"}]}' >/dev/null
  echo "harbor-pull ready in $ns"
done
