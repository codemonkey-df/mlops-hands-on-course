#!/usr/bin/env bash
# Shared helpers for exercise checks that run against the live cluster.
# Each check gets its own throw-away namespace that is deleted on exit.

ex_namespace() {
  # usage: ns=$(ex_namespace m01-bug01)
  local ns="ex-$1"
  kubectl delete namespace "$ns" --ignore-not-found --wait=true >/dev/null 2>&1
  kubectl create namespace "$ns" >/dev/null
  echo "$ns"
}

ex_cleanup() {
  kubectl delete namespace "$1" --ignore-not-found --wait=false >/dev/null 2>&1 || true
}

ex_curl() {
  # usage: ex_curl <namespace> <url>  -> runs curl from INSIDE the cluster
  kubectl -n "$1" run "curl-$RANDOM" --rm -i --restart=Never --quiet \
    --image=curlimages/curl:8.16.0 --command -- \
    curl -fsS --max-time 5 --retry 5 --retry-delay 2 --retry-all-errors "$2"
}

fail() { echo "FAIL: $*" >&2; exit 1; }
