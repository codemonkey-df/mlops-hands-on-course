#!/usr/bin/env bash
# Fix dagster.yaml in this folder, then: make check-m05 BUG=bug02
exec bash "$COURSE_ROOT/exercises/m05/_dagster_check.sh" "${1:-.}" m05-bug02
