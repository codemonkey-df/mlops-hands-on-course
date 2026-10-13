#!/usr/bin/env bash
# Fix the file in this folder, then: make check-m04 BUG=bug02
exec bash "$COURSE_ROOT/exercises/_py.sh" check.py "${1:-.}"
