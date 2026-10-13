#!/usr/bin/env bash
# Fix predictor.py in this folder, then: make check-m06 BUG=bug02
export BENTOML_DO_NOT_TRACK=true
exec bash "$COURSE_ROOT/exercises/_py.sh" check.py "${1:-.}"
