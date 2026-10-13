#!/usr/bin/env bash
# Fix servicemonitor.yaml in this folder, then: make check-m10 BUG=bug01
set -euo pipefail
uv run --project "$COURSE_ROOT" python "$COURSE_ROOT/exercises/m10/_prom_check.py" "${1:-.}/servicemonitor.yaml" servicemonitor
