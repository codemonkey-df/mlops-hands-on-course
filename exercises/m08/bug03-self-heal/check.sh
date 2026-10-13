#!/usr/bin/env bash
# Fix app.yaml in this folder, then: make check-m08 BUG=bug03
exec bash "$COURSE_ROOT/exercises/m08/_app_check.sh" "$(cd "${1:-.}" && pwd)" ex-m08-bug03 selfheal
