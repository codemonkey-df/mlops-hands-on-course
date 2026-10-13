#!/usr/bin/env bash
# Helpers for the M9 checks (sourced): one mock model + a LiteLLM router in a
# throw-away namespace. Uses the verified chart from reference/m09.
source "$COURSE_ROOT/exercises/_lib.sh"
CHART="$COURSE_ROOT/reference/m09/platform/charts/llm-model"
MOCK_TAG=$(grep -oE '"[^"]+" # ci:mock-vllm-tag' "$COURSE_ROOT/platform/gitops/llm-models/small-chat.yaml" 2>/dev/null | cut -d'"' -f2)
MOCK_TAG="${MOCK_TAG:-0.1.0}"

llm_ns() { # name -> namespace with pull + S3 secrets
  local ns; ns=$(ex_namespace "$1")
  "$COURSE_ROOT/infra/compose/harbor/k8s-pull-secret.sh" "$ns" >/dev/null
  kubectl -n "$ns" apply -f "$COURSE_ROOT/reference/m09/platform/gitops/llm/secrets.yaml" >/dev/null
  echo "$ns"
}

llm_model() { # ns release [helm args...]
  local ns="$1" rel="$2"; shift 2
  helm install -n "$ns" "$rel" "$CHART" --set image.mock.tag="$MOCK_TAG" \
    --set model.servedName="$rel" --set model.weightsPrefix="$rel" --set sim.loadSeconds=3 "$@" >/dev/null
}

llm_router() { # ns config.yaml
  kubectl -n "$1" create configmap litellm-config --from-file=config.yaml="$2" >/dev/null
  kubectl -n "$1" apply -f "$COURSE_ROOT/exercises/m09/_workload/litellm.yaml" >/dev/null
}

llm_chat() { # ns model -> prints "<served model> <content>" via the router (key stays in the pod)
  local pod; pod=$(kubectl -n "$1" get pod -l app=litellm -o name | head -1)
  kubectl -n "$1" cp "$COURSE_ROOT/exercises/m09/_workload/chat.py" "${pod#pod/}:/tmp/chat.py"
  kubectl -n "$1" exec "$pod" -- python /tmp/chat.py "$2"
}
