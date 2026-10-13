#!/usr/bin/env bash
# Configure Harbor through its REST API (idempotent):
#   - private project "mlops"
#   - tag immutability: a pushed tag can never be overwritten
#   - robot "ci"  (push+pull)  -> Gitea Actions secrets
#   - robot "k8s" (pull only)  -> imagePullSecret in the cluster
# Robot secrets are written to infra/compose/harbor/robots.env (git-ignored).
set -euo pipefail
cd "$(dirname "$0")"
LXC_IP="${LXC_IP:-$(hostname -I | awk '{print $1}')}"
API="http://$LXC_IP:8085/api/v2.0"
AUTH="admin:${HARBOR_ADMIN_PASSWORD:-Harbor-lab-12345}"
api() { curl -sS -u "$AUTH" -H 'Content-Type: application/json' "$@"; }

if [[ "$(api -o /dev/null -w '%{http_code}' "$API/projects?project_name=mlops" -I)" != "200" ]]; then
  api -X POST "$API/projects" -d '{"project_name":"mlops","metadata":{"public":"false"}}'
  echo "project mlops created"
fi
pid=$(api "$API/projects/mlops" | python3 -c 'import json,sys; print(json.load(sys.stdin)["project_id"])')

if [[ "$(api "$API/projects/mlops/immutabletagrules")" == "[]" ]]; then
  api -X POST "$API/projects/mlops/immutabletagrules" -d '{
    "disabled": false, "action": "immutable", "template": "immutable_template",
    "scope_selectors": {"repository": [{"kind": "doublestar", "decoration": "repoMatches", "pattern": "**"}]},
    "tag_selectors": [{"kind": "doublestar", "decoration": "matches", "pattern": "**"}]}'
  echo "immutability rule created"
fi

robot() { # name, actions-json  -> prints "robot$mlops+name secret"
  local name="$1" actions="$2" id
  id=$(api "$API/robots?q=name%3Dmlops%2B$name" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r[0]["id"] if r else "")')
  [[ -n "$id" ]] && api -X DELETE "$API/robots/$id" >/dev/null   # re-create = new secret
  api -X POST "$API/robots" -d "{
    \"name\": \"$name\", \"duration\": -1, \"level\": \"project\", \"description\": \"$name robot\",
    \"permissions\": [{\"kind\": \"project\", \"namespace\": \"mlops\", \"access\": $actions}]}" \
    | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["name"], r["secret"])'
}
read -r ci_user ci_secret < <(robot ci '[{"resource":"repository","action":"push"},{"resource":"repository","action":"pull"}]')
read -r k8s_user k8s_secret < <(robot k8s '[{"resource":"repository","action":"pull"}]')

umask 077
cat > robots.env <<EOF
HARBOR_CI_USER='$ci_user'
HARBOR_CI_SECRET='$ci_secret'
HARBOR_K8S_USER='$k8s_user'
HARBOR_K8S_SECRET='$k8s_secret'
EOF
echo "project id $pid; robots written to $(pwd)/robots.env"
