#!/usr/bin/env bash
# Operator checklist for the M11 loop. This does not inject drift for you
# (that is a Launchpad click so you see the UI); it prints the hops and
# the commands that prove each one moved.
set -euo pipefail
SERVER_IP="${SERVER_IP:-$(hostname -I | awk '{print $1}')}"

echo "== 1. current serving identity"
curl -sf "http://churn.${SERVER_IP}.nip.io:8080/model_info" | python -m json.tool || echo "(serving not reachable)"

echo
echo "== 2. inject drift in the Dagster UI"
echo "    http://dagster.${SERVER_IP}.nip.io:8080"
echo "    asset raw_customers → Launchpad → new partition, drift: 0.8"
echo "    then materialize clean_customers + drift_report for that partition"

echo
echo "== 3. sensor / training"
echo "    kubectl -n dagster get pods -w     # a run pod should appear"
echo "    MLflow: Models → churn-classifier → aliases champion / challenger"

echo
echo "== 4. release (promotion does NOT deploy)"
echo "    Gitea → Actions → ci → Run workflow"
echo "    git -C . log --oneline -5          # look for 'deploy: churn-bento ...'"

echo
echo "== 5. prove it landed"
echo "    kubectl -n serving rollout status deploy/churn"
echo "    curl -s http://churn.${SERVER_IP}.nip.io:8080/model_info"
echo "    Grafana → Churn API heatmap  (http://grafana.${SERVER_IP}.nip.io:8080)"

echo
echo "== 6. rollback"
echo "    git revert <the deploy commit> && git push gitea main"
