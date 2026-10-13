#!/usr/bin/env bash
# Install the chart, upgrade it twice, and require the password to stay the same.
# Fix chart/templates/secret.yaml, then: make check-m01 BUG=bug06
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
target="${1:-.}"
ns=$(ex_namespace m01-bug06); trap 'ex_cleanup "$ns"' EXIT
pw() { kubectl -n "$ns" get secret app-db -o jsonpath='{.data.password}' | base64 -d; }
helm install app "$target/chart" -n "$ns" >/dev/null
first=$(pw); [[ ${#first} -ge 16 ]] || fail "no generated password"
helm upgrade app "$target/chart" -n "$ns" >/dev/null
helm upgrade app "$target/chart" -n "$ns" >/dev/null
second=$(pw)
echo "install: $first"; echo "after 2 upgrades: $second"
[[ "$first" == "$second" ]] || fail "password changed on helm upgrade (clients would break)"
helm upgrade app "$target/chart" -n "$ns" --set auth.password=explicit >/dev/null
[[ "$(pw)" == "explicit" ]] || fail "explicit auth.password is ignored"
echo OK
