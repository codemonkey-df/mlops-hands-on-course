#!/usr/bin/env bash
# M11 has no new cluster components. Print the operator checklist.
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
bash "$root/reference/m11/scripts/capstone.sh"
