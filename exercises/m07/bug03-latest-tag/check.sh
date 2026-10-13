#!/usr/bin/env bash
# Fix release.sh in this folder, then: make check-m07 BUG=bug03
# Releases twice; the cluster must run each release's code.
set -euo pipefail
source "$COURSE_ROOT/exercises/m07/_harbor.sh"
target="${1:-.}"
harbor_login
ns=$(ex_namespace m07-bug03); trap 'ex_cleanup "$ns"' EXIT
pull_secret "$ns"
for n in 1 2; do
  v="v$(date +%s)-$RANDOM"
  image=$(bash "$target/release.sh" "$v" 2>&1) || fail "release $n failed: $(echo "$image" | tail -1)"
  out=$(run_pod "$ns" "hello-$n" "$image") || fail "release $n: pod failed"
  echo "release $n ($v) -> pod says: $out"
  [[ "$out" == "hello $v" ]] || fail "release $n: the cluster runs old code"
done
echo OK
