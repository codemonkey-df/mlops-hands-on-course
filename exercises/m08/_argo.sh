#!/usr/bin/env bash
# Helpers for the M8 checks (sourced): a throw-away Gitea repo + Argo apps.
source "$COURSE_ROOT/exercises/_lib.sh"
SERVER_IP="${SERVER_IP:-$(hostname -I | awk '{print $1}')}"
GITEA="http://$SERVER_IP:3300"
NETRC=$(mktemp); chmod 600 "$NETRC"
printf 'machine %s login mlops password %s\n' "$SERVER_IP" "${GITEA_ADMIN_PASSWORD:-mlops-gitea-secret}" > "$NETRC"
gapi() { curl -s --netrc-file "$NETRC" -H 'Content-Type: application/json' "$@"; }

ex_repo() { # name dir -> pushes dir as the repo's main branch (public repo)
  local name="$1" dir="$2" tmp
  gapi -o /dev/null -X DELETE "$GITEA/api/v1/repos/mlops/$name"
  gapi -o /dev/null -X POST "$GITEA/api/v1/user/repos" -d "{\"name\":\"$name\",\"private\":false,\"default_branch\":\"main\"}"
  tmp=$(mktemp -d); cp -r "$dir/." "$tmp/"; rm -rf "$tmp/.solution" "$tmp/check.sh"
  (cd "$tmp" && git init -q -b main && git add -A && git -c user.name=ex -c user.email=ex@lab commit -qm ex \
    && git -c credential.helper="!f() { echo username=mlops; echo password=${GITEA_ADMIN_PASSWORD:-mlops-gitea-secret}; }; f" \
       push -q "$GITEA/mlops/$name.git" main)
  rm -rf "$tmp"
}

ex_argo_cleanup() { # repo-name namespace app...
  local repo="$1" ns="$2"; shift 2
  for app in "$@"; do kubectl -n argocd delete application "$app" --ignore-not-found --wait=true --timeout=60s >/dev/null 2>&1 || true; done
  kubectl delete namespace "$ns" --ignore-not-found --wait=false >/dev/null 2>&1 || true
  kubectl delete crd modelcards.mlops.example.com --ignore-not-found >/dev/null 2>&1 || true
  gapi -o /dev/null -X DELETE "$GITEA/api/v1/repos/mlops/$repo"; rm -f "$NETRC"
}

app_state() { kubectl -n argocd get application "$1" -o jsonpath='{.status.sync.status}/{.status.health.status}' 2>/dev/null; }

wait_healthy() { # app timeout-seconds
  local app="$1" t="${2:-120}" s
  for _ in $(seq $((t / 5))); do
    s=$(app_state "$app"); [[ "$s" == "Synced/Healthy" ]] && return 0; sleep 5
  done
  echo "app $app is '$s'"
  kubectl -n argocd get application "$app" -o jsonpath='{range .status.conditions[*]}{.type}: {.message}{"\n"}{end}{.status.operationState.message}{"\n"}' 2>/dev/null | cut -c1-300
  return 1
}
