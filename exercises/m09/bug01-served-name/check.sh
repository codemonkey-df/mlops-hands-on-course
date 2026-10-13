#!/usr/bin/env bash
# Fix config.yaml in this folder, then: make check-m09 BUG=bug01
exec bash "$COURSE_ROOT/exercises/m09/_router_check.sh" "${1:-.}" m09-bug01
