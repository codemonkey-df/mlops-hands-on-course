#!/usr/bin/env bash
# Fix mlflow.yaml in this folder, then: make check-m03 BUG=bug03
exec bash "$COURSE_ROOT/exercises/m03/_mlflow_check.sh" "${1:-.}" m03-bug03
