#!/usr/bin/env bash
# M8 deploy: hand Dagster over from the Helm CLI to Argo CD, install Argo CD
# and the root app. Your repo (with platform/gitops/) must be pushed to Gitea.
set -euo pipefail
helm -n dagster uninstall dagster --wait 2>/dev/null || true   # Argo CD owns it from now on
platform/argocd/bootstrap.sh
echo "now: git add platform .gitea && git commit -m 'm08: gitops' && git push gitea main"
