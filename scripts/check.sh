#!/usr/bin/env bash
# Run the break/fix verifiers of one module.
#   scripts/check.sh m01          -> every bug of module 1
#   scripts/check.sh m01 bug02    -> only one bug
# Each exercises/<module>/<bug>/check.sh receives the directory to verify as $1.
set -uo pipefail

module="${1:?usage: check.sh mNN [bugNN]}"
only="${2:-}"
root="$(cd "$(dirname "$0")/.." && pwd)"
export COURSE_ROOT="$root"
dir="$root/exercises/$module"
[[ -d "$dir" ]] || { echo "no exercises for $module"; exit 1; }

pass=0; fail=0
for bug in "$dir"/bug*/; do
  name="$(basename "$bug")"
  [[ -n "$only" && "$name" != "$only"* ]] && continue
  if (cd "$bug" && bash ./check.sh "$bug" >"/tmp/check-$module-$name.log" 2>&1); then
    echo "  PASS  $module/$name"; pass=$((pass + 1))
  else
    echo "  FAIL  $module/$name   (log: /tmp/check-$module-$name.log)"; fail=$((fail + 1))
  fi
done
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]]
