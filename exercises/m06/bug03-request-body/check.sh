#!/usr/bin/env bash
# Fix client.py in this folder, then: make check-m06 BUG=bug03
exec bash "$COURSE_ROOT/exercises/_py.sh" check.py "${1:-.}"
