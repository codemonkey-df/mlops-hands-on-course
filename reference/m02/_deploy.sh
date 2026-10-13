#!/usr/bin/env bash
# M2 deploy: generate data into MinIO, set up DVC with the MinIO remote, repro + push.
set -euo pipefail
[[ -f .env ]] || cp .env.example .env
set -a; source .env; set +a

uv run python -m mlops_course.data.cli --out s3://datasets --days 3

[[ -d .dvc ]] || dvc init -q
dvc remote add -d -f minio s3://dvc/store
dvc remote modify minio endpointurl "$S3_ENDPOINT_URL"
dvc remote modify --local minio access_key_id "$S3_ACCESS_KEY"
dvc remote modify --local minio secret_access_key "$S3_SECRET_KEY"
dvc repro
dvc push
