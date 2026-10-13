#!/usr/bin/env bash
# Maintainer self-test for break/fix exercises:
#   1. the broken files must FAIL their check
#   2. the same files with .solution/ overlaid must PASS
# Usage: scripts/verify-exercises.sh m01
set -uo pipefail

module="${1:?usage: verify-exercises.sh mNN}"
root="$(cd "$(dirname "$0")/.." && pwd)"
export COURSE_ROOT="$root"
ok=1
for bug in "$root/exercises/$module"/bug*/; do
  name="$(basename "$bug")"
  if (cd "$bug" && bash ./check.sh "$bug" >/dev/null 2>&1); then
    echo "  WRONG  $name: broken version passes"; ok=0
  else
    echo "  ok     $name: broken version fails"
  fi
  work="$(mktemp -d)"
  cp -r "$bug"/. "$work"/
  cp -r "$bug"/.solution/. "$work"/
  if (cd "$work" && bash ./check.sh "$work" >"/tmp/verify-$module-$name.log" 2>&1); then
    echo "  ok     $name: solution passes"
  else
    echo "  WRONG  $name: solution fails (log: /tmp/verify-$module-$name.log)"; ok=0
  fi
  rm -rf "$work"
done
[[ $ok -eq 1 ]]
