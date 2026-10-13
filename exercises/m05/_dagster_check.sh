#!/usr/bin/env bash
# Shared check for the Dagster-on-k8s exercises:
#   1. install the dagster chart with $1/dagster.yaml into a fresh namespace
#      (own Postgres database, no Ingress)
#   2. all Deployments become Ready (fails fast on CrashLoop / config errors)
#   3. launch daily_ingest for one partition -> the run Job must complete
set -euo pipefail
source "$COURSE_ROOT/exercises/_lib.sh"
target="$1"; name="$2"
db="ex_${name//-/_}"
psql() { kubectl -n storage exec postgres-0 -- psql -U mlops -d postgres -qc "$1" >/dev/null; }

ns=$(ex_namespace "$name")
trap 'helm -n "$ns" uninstall dagster --wait >/dev/null 2>&1 || true; ex_cleanup "$ns"; psql "DROP DATABASE IF EXISTS $db WITH (FORCE)" || true' EXIT
psql "DROP DATABASE IF EXISTS $db WITH (FORCE)"; psql "CREATE DATABASE $db"
sed "s/namespace: dagster/namespace: $ns/" "$COURSE_ROOT/reference/m05/platform/k8s/dagster/10-secrets.yaml" \
  | kubectl apply -f - >/dev/null

echo "--- helm install ($ns)"
helm -n "$ns" install dagster dagster/dagster --version 1.13.26 -f "$target/dagster.yaml" \
  --set ingress.enabled=false --set postgresql.postgresqlDatabase="$db" >/dev/null \
  || fail "helm install rejected the values"

pod_problem() {
  kubectl -n "$ns" get pods -o jsonpath='{range .items[*]}{.metadata.name}{" "}{range .status.initContainerStatuses[*]}{.state.waiting.reason}{" "}{end}{range .status.containerStatuses[*]}{.state.waiting.reason}{" "}{end}{"\n"}{end}' \
    | grep -E "CrashLoopBackOff|CreateContainerConfigError|ErrImagePull|ImagePullBackOff|Error" || true
}

echo "--- waiting for webserver, daemon and code server"
for _ in $(seq 60); do
  bad=$(pod_problem); [[ -n "$bad" ]] && { kubectl -n "$ns" get pods; fail "pod problem: $bad"; }
  ready=$(kubectl -n "$ns" get deploy -o jsonpath='{range .items[?(@.status.readyReplicas==1)]}x{end}')
  [[ "$ready" == "xxx" ]] && break
  sleep 5
done
[[ "${ready:-}" == "xxx" ]] || { kubectl -n "$ns" get pods; fail "webserver/daemon/code server not ready"; }

echo "--- launch daily_ingest, partition 2026-10-05"
kubectl -n "$ns" exec deploy/dagster-dagster-webserver -c dagster -- \
  dagster job launch -w /dagster-workspace/workspace.yaml -l churn -j daily_ingest \
  --tags '{"dagster/partition": "2026-10-05"}' >/dev/null 2>&1 || fail "could not submit the run"

for _ in $(seq 24); do
  job=$(kubectl -n "$ns" get jobs -o name | head -1); [[ -n "$job" ]] && break; sleep 5
done
[[ -n "${job:-}" ]] || { kubectl -n "$ns" logs deploy/dagster-daemon --tail=20; fail "no run Job was created"; }
echo "run Job: $job"
for _ in $(seq 60); do
  bad=$(pod_problem); [[ -n "$bad" ]] && fail "run pod problem: $bad"
  st=$(kubectl -n "$ns" get "$job" -o jsonpath='{.status.succeeded}/{.status.failed}')
  [[ "$st" == 1/* ]] && { echo OK; exit 0; }
  [[ "$st" == */[1-9]* ]] && { kubectl -n "$ns" logs "$job" --tail=15 | cut -c1-300; fail "run failed"; }
  sleep 5
done
fail "run did not finish in time"
