#!/usr/bin/env bash
# Shared check for bug01/bug02: model "small-chat" + router with ./config.yaml.
set -euo pipefail
source "$COURSE_ROOT/exercises/m09/_llm.sh"
dir="$1" name="$2"
ns=$(llm_ns "$name"); trap 'ex_cleanup "$ns"' EXIT
llm_model "$ns" small-chat
llm_router "$ns" "$dir/config.yaml"
kubectl -n "$ns" rollout status deploy/small-chat --timeout=180s >/dev/null || fail "model not ready"
kubectl -n "$ns" rollout status deploy/litellm --timeout=240s >/dev/null || fail "router not ready"
out=$(llm_chat "$ns" small-chat) || fail "router call failed: $out"
echo "$out"
[[ "$out" == "small-chat [small-chat]"* ]] || fail "unexpected answer"
echo OK
