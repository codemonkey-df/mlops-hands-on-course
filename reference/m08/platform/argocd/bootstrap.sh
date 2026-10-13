#!/usr/bin/env bash
# Install Argo CD, give it read access to the Gitea repo, apply the root app.
set -euo pipefail
cd "$(dirname "$0")/../.."
LXC_IP="${LXC_IP:-$(hostname -I | awk '{print $1}')}"
GITEA="http://$LXC_IP:3300"
GITEA_PW="${GITEA_ADMIN_PASSWORD:-mlops-gitea-secret}"

helm repo add argo https://argoproj.github.io/argo-helm >/dev/null 2>&1 || true
helm upgrade --install argocd argo/argo-cd --version 10.10.3 -n argocd --create-namespace \
  -f platform/argocd/values.yaml --wait --timeout 10m

# Read-only Gitea token for Argo CD (re-created on every run).
netrc=$(mktemp); trap 'rm -f "$netrc"' EXIT; chmod 600 "$netrc"
printf 'machine %s login mlops password %s\n' "$LXC_IP" "$GITEA_PW" > "$netrc"
curl -s --netrc-file "$netrc" -X DELETE "$GITEA/api/v1/users/mlops/tokens/argocd" >/dev/null || true
token=$(curl -s --netrc-file "$netrc" -H 'Content-Type: application/json' -X POST \
  "$GITEA/api/v1/users/mlops/tokens" -d '{"name":"argocd","scopes":["read:repository"]}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["sha1"])')

# Declarative repository credentials: a Secret with this label.
kubectl -n argocd apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: repo-mlops
  labels: { argocd.argoproj.io/secret-type: repository }
stringData:
  type: git
  url: $GITEA/mlops/mlops.git
  username: mlops
  password: $token
EOF

kubectl apply -f platform/argocd/root-app.yaml
echo "UI: http://argocd.$LXC_IP.nip.io:8080  user admin, password:"
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
