#!/usr/bin/env bash
# Fix ci.yaml in this folder, then: make check-m07 BUG=bug05
target="$(cd "${1:-.}" && pwd)"
exec bash "$COURSE_ROOT/exercises/_py.sh" "$COURSE_ROOT/exercises/m07/_wf_check.py" "$target"
