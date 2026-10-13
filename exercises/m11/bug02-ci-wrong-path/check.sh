#!/usr/bin/env bash
set -euo pipefail
uv run --project "$COURSE_ROOT" python "$COURSE_ROOT/exercises/m11/_incident_check.py" "${1:-.}/ci.yaml" ci
