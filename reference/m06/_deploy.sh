#!/usr/bin/env bash
# M6 deploy: import @champion from MLflow, build + containerize the Bento,
# import it into k3d and roll out the churn API.
set -euo pipefail
set -a; source .env; set +a

tag=$(uv run python -m mlops_course.serving.import_model --alias champion 2>&1 | grep -oE "churn-classifier:mv[0-9]+" | tail -1)
ver="${tag#churn-classifier:}"                     # e.g. mv7
uv run bentoml build -f platform/bento/bentofile.yaml src --version "$ver"
uv run bentoml containerize "churn:$ver" -t "mlops/churn-bento:$ver"
k3d image import "mlops/churn-bento:$ver" -c mlops
sed "s|mlops/churn-bento:mv[0-9]*|mlops/churn-bento:$ver|" platform/k8s/serving/churn.yaml | kubectl apply -f -
kubectl -n serving rollout status deploy/churn --timeout=300s
curl -s -X POST http://churn.192.168.1.202.nip.io:8080/model_info; echo
