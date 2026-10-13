#!/usr/bin/env bash
# Fix the file in this folder, then: make check-m03 BUG=bug05
exec bash "$COURSE_ROOT/exercises/_py.sh" check.py "${1:-.}"
