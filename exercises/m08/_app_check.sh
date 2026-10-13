#!/usr/bin/env bash
# Shared check for bug01-03: push this folder as a Gitea repo, apply app.yaml,
# the app must become Synced/Healthy. With "selfheal": manual drift must be reverted.
set -euo pipefail
source "$COURSE_ROOT/exercises/m08/_argo.sh"
target="$1"; name="$2"; mode="${3:-}"
repo="$name"; ns="$name"
trap 'ex_argo_cleanup "$repo" "$ns" "$name"' EXIT
ex_repo "$repo" "$target"
sed "s/__REPO__/$repo/; s/__NS__/$ns/" "$target/app.yaml" | kubectl apply -f - >/dev/null
wait_healthy "$name" 120 || fail "application never became Synced/Healthy"
if [[ "$mode" == selfheal ]]; then
  echo "--- manual drift: kubectl scale --replicas=4"
  kubectl -n "$ns" scale deploy/hello --replicas=4 >/dev/null
  for _ in $(seq 12); do
    sleep 5; r=$(kubectl -n "$ns" get deploy hello -o jsonpath='{.spec.replicas}')
    [[ "$r" == 2 ]] && { echo "reverted to Git (replicas=2)"; echo OK; exit 0; }
  done
  fail "replicas still $r: the cluster drifted from Git and nobody fixed it"
fi
echo OK
