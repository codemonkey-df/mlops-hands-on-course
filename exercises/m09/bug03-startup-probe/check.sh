#!/usr/bin/env bash
# Fix probes.yaml in this folder, then: make check-m09 BUG=bug03
# The model takes 30 s to load (like a real one, only shorter).
set -euo pipefail
source "$COURSE_ROOT/exercises/m09/_llm.sh"
ns=$(llm_ns m09-bug03); trap 'ex_cleanup "$ns"' EXIT
llm_model "$ns" small-chat --set sim.loadSeconds=30 -f "${1:-.}/probes.yaml"
kubectl -n "$ns" rollout status deploy/small-chat --timeout=150s || fail "model never became ready"
restarts=$(kubectl -n "$ns" get pod -l app.kubernetes.io/instance=small-chat \
  -o jsonpath='{.items[0].status.containerStatuses[0].restartCount}')
[[ "$restarts" == "0" ]] || fail "container restarted $restarts times while loading"
echo OK
