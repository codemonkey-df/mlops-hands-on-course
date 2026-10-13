#!/usr/bin/env bash
# Shared check for M1 manifest bugs: apply $1/app.yaml in a fresh namespace,
# require a clean rollout without restarts, then call MinIO through the Service.
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
target="$1"; name="$2"

ns=$(ex_namespace "$name")
trap 'ex_cleanup "$ns"' EXIT

kubectl -n "$ns" apply -f "$target/app.yaml" || fail "apply rejected"
kubectl -n "$ns" rollout status deploy/minio --timeout=90s || {
  kubectl -n "$ns" get pods -o wide
  kubectl -n "$ns" describe pods | tail -25
  fail "deployment never became ready"
}
restarts=$(kubectl -n "$ns" get pods -l app.kubernetes.io/name=minio \
  -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}')
[[ "$restarts" == "0" ]] || fail "container restarted $restarts times"

kubectl -n "$ns" get endpointslices -l kubernetes.io/service-name=minio -o wide
ex_curl "$ns" "http://minio:9000/minio/health/ready" >/dev/null \
  || fail "Service minio:9000 does not reach the pod"
echo OK
