#!/usr/bin/env bash
# Start Gitea, create the admin user + "mlops" repo, register the runner and
# store the Harbor robot credentials as repository Actions secrets.
# Idempotent: safe to re-run.
set -euo pipefail
cd "$(dirname "$0")"
export LXC_IP="${LXC_IP:-$(hostname -I | awk '{print $1}')}"
GITEA="http://$LXC_IP:3300"
ADMIN=mlops
ADMIN_PASS="${GITEA_ADMIN_PASSWORD:-mlops-gitea-secret}"
ROOT="$(cd ../../.. && pwd)"

docker build -q -t mlops/ci-runner:1 "$ROOT/platform/images/ci-runner" >/dev/null
docker compose up -d gitea
until curl -sf "$GITEA/api/healthz" >/dev/null; do sleep 2; done

gt() { docker compose exec -T -u git gitea gitea "$@"; }
gt admin user create --admin --username "$ADMIN" --password "$ADMIN_PASS" \
   --email mlops@example.local --must-change-password=false 2>/dev/null || true
api() { curl -sS -u "$ADMIN:$ADMIN_PASS" -H 'Content-Type: application/json' "$@"; }
api -o /dev/null -X POST "$GITEA/api/v1/user/repos" -d '{"name":"mlops","private":true,"default_branch":"main"}' || true

# Runner registration token (only used the first time; .runner persists).
export RUNNER_TOKEN; RUNNER_TOKEN="$(gt actions generate-runner-token | tail -1)"
docker compose up -d runner

# Harbor robot -> Actions secrets (values never appear in the workflow file).
# shellcheck disable=SC1091
source "$ROOT/infra/compose/harbor/robots.env"
secret() { api -o /dev/null -w "secret $1: %{http_code}\n" -X PUT \
  "$GITEA/api/v1/repos/$ADMIN/mlops/actions/secrets/$1" -d "$(python3 -c 'import json,sys; print(json.dumps({"data": sys.argv[1]}))' "$2")"; }
secret HARBOR_USER "$HARBOR_CI_USER"
secret HARBOR_PASSWORD "$HARBOR_CI_SECRET"
secret MLFLOW_TRACKING_URI "http://mlflow.$LXC_IP.nip.io:8080"

echo "Gitea: $GITEA  (user $ADMIN)"
echo "git remote add gitea http://$ADMIN:<password>@$LXC_IP:3300/$ADMIN/mlops.git"
