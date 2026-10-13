#!/usr/bin/env bash
# Fix push.sh in this folder, then: make check-m07 BUG=bug01
set -euo pipefail
source "$COURSE_ROOT/exercises/m07/_harbor.sh"
target="${1:-.}"
for r in 127.0.0.1:8085 YOUR_SERVER_IP:8085; do printf '%s' "$HARBOR_CI_SECRET" | docker login "$r" -u "$HARBOR_CI_USER" --password-stdin >/dev/null 2>&1 || true; done
bash "$target/push.sh" busybox:1.37 "ex-push:$(date +%s)-$RANDOM" || fail "push failed"
echo OK
