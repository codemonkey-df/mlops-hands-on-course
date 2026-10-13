#!/usr/bin/env bash
# Run a Python exercise check with the course reference packages importable
# and the lab S3 credentials from .env exported.
set -euo pipefail
set -a; [[ -f "$COURSE_ROOT/.env" ]] && source "$COURSE_ROOT/.env"; set +a
export PYTHONPATH="$COURSE_ROOT/exercises:$(ls -d "$COURSE_ROOT"/reference/m*/src | tr '\n' ':')"
exec uv run --project "$COURSE_ROOT" python "$@"
