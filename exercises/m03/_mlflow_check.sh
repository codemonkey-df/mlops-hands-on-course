#!/usr/bin/env bash
# Shared check for the MLflow server exercises:
#   1. deploy $1/mlflow.yaml into a fresh namespace
#   2. an in-cluster client WITHOUT S3 credentials logs an artifact and reads it back
#   3. the server answers API calls through the Ingress hostname
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
target="$1"; name="$2"
host="mlflow-$name.$(hostname -I | awk '{print $1}').nip.io"

ns=$(ex_namespace "$name"); trap 'ex_cleanup "$ns"' EXIT
kubectl -n "$ns" create secret generic s3 \
  --from-literal=AWS_ACCESS_KEY_ID=mlops --from-literal=AWS_SECRET_ACCESS_KEY=mlops-minio-secret >/dev/null
sed "s/__HOST__/$host/g" "$target/mlflow.yaml" | kubectl -n "$ns" apply -f -
kubectl -n "$ns" rollout status deploy/mlflow --timeout=180s || fail "server not ready"

echo "--- client: log + download an artifact (no S3 credentials on purpose)"
kubectl -n "$ns" run client --rm -i --restart=Never --quiet --image=mlops/mlflow:3.17.1-2 \
  --image-pull-policy=IfNotPresent --command -- python -c '
import mlflow, tempfile, pathlib
mlflow.set_tracking_uri("http://mlflow:5000")
with mlflow.start_run() as run:
    mlflow.log_text("hello", "hello.txt")
d = mlflow.artifacts.download_artifacts(run_id=run.info.run_id, artifact_path="hello.txt")
assert pathlib.Path(d).read_text() == "hello"
print("artifact roundtrip OK")
' || fail "client could not log/read artifacts"

echo "--- API through the ingress ($host)"
code=$(curl -s -o /tmp/mlflow-ingress-body -w '%{http_code}' --retry 5 --retry-delay 2 --retry-all-errors \
  "http://$host:8080/api/2.0/mlflow/experiments/search?max_results=1")
[[ "$code" == "200" ]] || { cat /tmp/mlflow-ingress-body; fail "ingress API returned $code"; }
echo OK
