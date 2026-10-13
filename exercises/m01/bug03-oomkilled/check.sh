#!/usr/bin/env bash
# Fix app.yaml in this folder, then: make check-m01 BUG=bug03
exec bash "$COURSE_ROOT/exercises/m01/_app_check.sh" "${1:-.}" m01-bug03
