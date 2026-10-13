#!/usr/bin/env bash
# Fix bentofile.yaml in this folder, then: make check-m06 BUG=bug01
# Builds a Bento from your bentofile, then loads the model with the Bento's
# src/ FIRST on sys.path, exactly like the container does.
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
target="$(cd "${1:-.}" && pwd)"; ver="ex-m06-bug01-$RANDOM"
export BENTOML_DO_NOT_TRACK=true
bml() { uv run --project "$COURSE_ROOT" bentoml "$@"; }
ctx=$(mktemp -d); trap 'rm -rf "$ctx"; bml delete "churn:$ver" -y >/dev/null 2>&1 || true' EXIT
cp -r "$COURSE_ROOT/reference/m03/src/." "$COURSE_ROOT/reference/m06/src/." "$ctx/"
touch "$ctx/mlops_course/__init__.py"   # a regular package, like src/mlops_course
bml build -f "$target/bentofile.yaml" "$ctx" --version "$ver" >/dev/null || fail "bentoml build failed"
bento="$(bml get "churn:$ver" -o path 2>/dev/null | tail -1)"
echo "bento src: $(cd "$bento/src" && find . -name '*.py' | sort | tr '\n' ' ')"
cd "$bento/src"
PYTHONPATH="$bento/src" uv run --project "$COURSE_ROOT" python -c '
import logging, bentoml
logging.disable(logging.WARNING)
from mlops_course.serving.service import ChurnService  # what the server imports first
m = bentoml.mlflow.load_model("churn-classifier:latest")
print("model loaded:", type(m).__name__)
' 2>&1 | grep -E "Error|loaded" || true
PYTHONPATH="$bento/src" uv run --project "$COURSE_ROOT" python -c '
import logging, bentoml
logging.disable(logging.WARNING)
from mlops_course.serving.service import ChurnService
bentoml.mlflow.load_model("churn-classifier:latest")' >/dev/null 2>&1 || fail "the model cannot be loaded from this Bento"
echo OK
