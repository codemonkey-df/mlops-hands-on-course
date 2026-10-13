#!/usr/bin/env bash
# Fix churn.yaml in this folder, then: make check-m06 BUG=bug04
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
ns=$(ex_namespace m06-bug04); trap 'ex_cleanup "$ns"' EXIT
kubectl -n "$ns" apply -f "${1:-.}/churn.yaml" >/dev/null
kubectl -n "$ns" rollout status deploy/churn --timeout=180s || fail "deployment not ready"
ex_curl "$ns" "http://churn:3000/readyz" || fail "Service churn:3000 does not reach the BentoML server"
echo OK
