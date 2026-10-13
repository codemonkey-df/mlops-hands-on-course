#!/usr/bin/env bash
# Fix image.txt (the image reference a pod uses), then: make check-m07 BUG=bug02
set -euo pipefail
source "$COURSE_ROOT/exercises/m07/_harbor.sh"
target="${1:-.}"
harbor_login; docker tag busybox:1.37 127.0.0.1:8085/mlops/smoke:1
docker push -q 127.0.0.1:8085/mlops/smoke:1 >/dev/null 2>&1 || true   # exists already = fine
ns=$(ex_namespace m07-bug02); trap 'ex_cleanup "$ns"' EXIT
pull_secret "$ns"
image="$(tr -d '[:space:]' < "$target/image.txt")"
kubectl -n "$ns" run smoke --image="$image" --restart=Never --command -- echo pulled >/dev/null
for _ in $(seq 30); do
  [[ "$(kubectl -n "$ns" get pod smoke -o jsonpath='{.status.phase}')" == Succeeded ]] && { echo OK; exit 0; }
  reason=$(kubectl -n "$ns" get pod smoke -o jsonpath='{.status.containerStatuses[0].state.waiting.reason}')
  if [[ "$reason" == *Image* || "$reason" == ErrImagePull ]]; then
    kubectl -n "$ns" get events --field-selector involvedObject.name=smoke -o jsonpath='{range .items[*]}{.message}{"\n"}{end}' | grep -i fail | tail -1 | cut -c1-300
    fail "the cluster cannot pull $image"
  fi
  sleep 2
done
fail "pod did not finish"
