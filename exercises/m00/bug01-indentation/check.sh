#!/usr/bin/env bash
# Verifies $1/cluster.yaml.tpl (default: this folder). Run via: make check-m00
set -euo pipefail
target="${1:-.}"
uv run --project "$COURSE_ROOT" python "$COURSE_ROOT/exercises/m00/_k3d_check.py" "$target/cluster.yaml.tpl" structure
