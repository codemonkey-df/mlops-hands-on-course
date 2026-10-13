#!/usr/bin/env bash
# M9 deploy: mock-vllm image -> Harbor, fake weights -> MinIO, pull secret for
# the llm namespace. Argo CD deploys the rest once you push platform/.
set -euo pipefail
# shellcheck disable=SC1091
source infra/compose/harbor/robots.env
printf '%s' "$HARBOR_CI_SECRET" | docker login 127.0.0.1:8085 -u "$HARBOR_CI_USER" --password-stdin >/dev/null
docker build -q -f platform/images/mock-vllm/Dockerfile -t 127.0.0.1:8085/mlops/mock-vllm:0.1.0 .
docker push -q 127.0.0.1:8085/mlops/mock-vllm:0.1.0
uv run python -m mlops_course.llm.fake_weights small-chat --size-mb 20 --max-len 4096
uv run python -m mlops_course.llm.fake_weights big-reasoning --size-mb 80 --max-len 16384
infra/compose/harbor/k8s-pull-secret.sh llm
echo "now: git add platform src tests .gitea && git commit -m 'm09: llm' && git push gitea main"
