#!/usr/bin/env bash
# Fix the files in apps/, then: make check-m08 BUG=bug04
# A root app (app-of-apps) syncs apps/; both child apps must end up Healthy.
set -euo pipefail
source "$COURSE_ROOT/exercises/m08/_argo.sh"
target="$(cd "${1:-.}" && pwd)"; repo=ex-m08-bug04; ns=ex-m08-bug04
trap 'ex_argo_cleanup "$repo" "$ns" ex-m08-bug04-root ex-m08-bug04-cards ex-m08-bug04-crds' EXIT
ex_repo "$repo" "$target"
kubectl apply -f - >/dev/null <<YAML
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: ex-m08-bug04-root, namespace: argocd }
spec:
  project: default
  source: { repoURL: "http://192.168.1.202:3300/mlops/$repo.git", targetRevision: main, path: apps }
  destination: { server: "https://kubernetes.default.svc", namespace: argocd }
  syncPolicy: { automated: { prune: true } }
YAML
wait_healthy ex-m08-bug04-crds 150 && wait_healthy ex-m08-bug04-cards 60 || fail "app-of-apps did not converge"
kubectl -n "$ns" get modelcard churn-classifier >/dev/null && echo OK
