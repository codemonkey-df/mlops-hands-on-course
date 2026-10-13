#!/usr/bin/env bash
# M3 deploy: build + import the MLflow image, deploy the server, train two
# models, register both and promote the better one to @champion.
set -euo pipefail
set -a; source .env; set +a

docker build -t mlops/mlflow:3.17.1-2 platform/images/mlflow
k3d image import mlops/mlflow:3.17.1-2 -c mlops
kubectl apply -f platform/k8s/mlflow/
kubectl -n mlflow rollout status deploy/mlflow --timeout=300s
until curl -sf "$MLFLOW_TRACKING_URI/health" >/dev/null; do sleep 2; done

for model in logreg mlp; do
  run_id=$(uv run python -c "
import logging, sys
from mlops_course.data.config import S3Settings
from mlops_course.training.train import TrainConfig, load_training_data, train
logging.disable(logging.CRITICAL)
print(train(load_training_data(S3Settings()), TrainConfig(model='$model', epochs=15)).run_id)
" 2>/dev/null | tail -1)
  uv run python -m mlops_course.training.registry register --run-id "$run_id"
  uv run python -m mlops_course.training.registry promote
done
uv run python -m mlops_course.training.registry show
