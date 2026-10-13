#!/usr/bin/env bash
# M7 deploy: Harbor + robots, Gitea + runner + secrets, pull secrets in k3d.
# Pushing YOUR repo to Gitea stays a manual step (see the module page).
set -euo pipefail
infra/compose/harbor/setup.sh
infra/compose/harbor/bootstrap.sh
infra/compose/gitea/setup.sh
infra/compose/harbor/k8s-pull-secret.sh serving dagster
