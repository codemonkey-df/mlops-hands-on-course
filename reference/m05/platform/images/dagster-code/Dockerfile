# User-code image: our Dagster definitions + every library the assets import.
# The SAME image runs (1) the gRPC code server the webserver talks to and
# (2) every run pod launched by the K8sRunLauncher.
#
# Build from the repo root:  docker build -f platform/images/dagster-code/Dockerfile -t mlops/dagster-code:0.1.0 .
FROM ghcr.io/astral-sh/uv:0.11.3 AS uv

FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /opt/dagster/app

# 1. Dependencies only (cached layer: changes only when uv.lock changes).
COPY pyproject.toml uv.lock README.md ./
# The cache mount keeps uv's download cache OUT of the image (saves ~2 GB).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 2. Our code, installed as a regular (non-editable) package.
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Dagster needs a writable DAGSTER_HOME; the instance config itself is
# injected by the Helm chart (ConfigMap mounted at $DAGSTER_HOME/dagster.yaml).
ENV DAGSTER_HOME=/opt/dagster/dagster_home
RUN mkdir -p $DAGSTER_HOME && useradd -u 1000 -m dagster && chown -R dagster $DAGSTER_HOME
USER 1000
