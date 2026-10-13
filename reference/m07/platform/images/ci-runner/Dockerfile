# Job image for Gitea Actions: everything our workflows need, nothing pulled
# at job time. Build once:  docker build -t mlops/ci-runner:1 platform/images/ci-runner
FROM docker:29-cli AS docker
FROM docker/buildx-bin:0.33.0 AS buildx
FROM ghcr.io/astral-sh/uv:0.11.3 AS uv

FROM python:3.12-slim
# git: checkout.  curl/jq: API calls.  gettext-base: envsubst.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git curl jq gettext-base ca-certificates \
 && rm -rf /var/lib/apt/lists/*
# The Docker CLI talks to the HOST daemon through the mounted socket.
COPY --from=docker /usr/local/bin/docker /usr/local/bin/docker
COPY --from=buildx /buildx /usr/local/lib/docker/cli-plugins/docker-buildx
COPY --from=uv /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy UV_CACHE_DIR=/cache/uv
