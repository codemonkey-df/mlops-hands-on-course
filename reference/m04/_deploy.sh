#!/usr/bin/env bash
# M4 deploy: materialize 3 clean days + reference profile + drift reports
# into s3://dagster with the local Dagster instance in .dagster_home/.
set -euo pipefail
set -a; source .env; set +a
export DAGSTER_HOME="$PWD/.dagster_home"
mkdir -p "$DAGSTER_HOME"
M=(-m mlops_course.pipelines.definitions)

for day in 2026-10-01 2026-10-02 2026-10-03; do
  uv run dagster asset materialize "${M[@]}" --select raw_customers,clean_customers --partition "$day"
done
uv run dagster asset materialize "${M[@]}" --select reference_profile
for day in 2026-10-02 2026-10-03; do
  uv run dagster asset materialize "${M[@]}" --select drift_report --partition "$day"
done
echo "Now run: DAGSTER_HOME=\$PWD/.dagster_home uv run dagster dev ${M[*]} -h 0.0.0.0 -p 3000"
