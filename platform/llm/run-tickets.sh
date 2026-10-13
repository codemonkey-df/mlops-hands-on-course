#!/usr/bin/env bash
# Run the ticket client INSIDE the cluster as a one-off Job:
#   platform/llm/run-tickets.sh [N] [CONCURRENCY] [DRIFT]
# It uses the Dagster code image (it contains mlops_course) and reads the
# router key straight from the Secret, so the key never leaves the cluster.
set -euo pipefail
N="${1:-20}" CONC="${2:-4}" DRIFT="${3:-0}"
TAG=$(grep -oE '"[^"]+" # ci:dagster-tag' platform/gitops/dagster/values.yaml | cut -d'"' -f2)
NAME="tickets-$(date +%s)"
kubectl -n llm apply -f - <<YAML
apiVersion: batch/v1
kind: Job
metadata: {name: $NAME}
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 600
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: client
          image: harbor.local:8085/mlops/dagster-code:$TAG
          command: [python, -m, mlops_course.llm.client, --n, "$N", --concurrency, "$CONC", --drift, "$DRIFT"]
          env:
            - {name: LLM_BASE_URL, value: "http://litellm.llm.svc.cluster.local:4000/v1"}
            - name: LLM_API_KEY
              valueFrom: {secretKeyRef: {name: litellm, key: LITELLM_MASTER_KEY}}
YAML
kubectl -n llm wait --for=condition=complete --timeout=600s "job/$NAME" \
  || kubectl -n llm wait --for=condition=failed --timeout=5s "job/$NAME" || true
kubectl -n llm logs "job/$NAME"
