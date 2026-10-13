#!/usr/bin/env bash
# Render the chart, validate it against the real API server (dry-run) and
# check the label value. Fix files under chart/, then: make check-m01 BUG=bug05
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
target="${1:-.}"
ns=$(ex_namespace m01-bug05); trap 'ex_cleanup "$ns"' EXIT
rendered=$(helm template typed "$target/chart" -n "$ns") || fail "helm template failed"
echo "$rendered"
echo "$rendered" | kubectl -n "$ns" apply --dry-run=server -f - || fail "API server rejected the manifest"
echo "$rendered" | grep -q 'pg-version: "17.10"' || fail "label pg-version is not \"17.10\""
echo OK
