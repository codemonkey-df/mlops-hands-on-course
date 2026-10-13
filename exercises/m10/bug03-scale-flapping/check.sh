#!/usr/bin/env bash
set -euo pipefail
uv run --project "$COURSE_ROOT" python "$COURSE_ROOT/exercises/m10/_prom_check.py" "${1:-.}/scaledobject.yaml" stability
