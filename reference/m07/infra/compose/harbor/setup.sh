#!/usr/bin/env bash
# Install / start Harbor with Docker Compose (online installer: images are
# pulled from Docker Hub on first install).
#
#   infra/compose/harbor/setup.sh          install (or re-configure) + start
#   cd infra/compose/harbor/installer && docker compose stop|start|down
set -euo pipefail
cd "$(dirname "$0")"
VERSION=v2.15.4
export LXC_IP="${LXC_IP:-$(hostname -I | awk '{print $1}')}"
export HARBOR_DATA="${HARBOR_DATA:-$HOME/.local/share/harbor}"
# Lab passwords. Override via env; never commit real ones.
export HARBOR_ADMIN_PASSWORD="${HARBOR_ADMIN_PASSWORD:-Harbor-lab-12345}"
export HARBOR_DB_PASSWORD="${HARBOR_DB_PASSWORD:-harbor-db-secret}"

if [[ ! -x installer/install.sh ]]; then
  mkdir -p installer
  curl -fsSL "https://github.com/goharbor/harbor/releases/download/$VERSION/harbor-online-installer-$VERSION.tgz" \
    | tar xz -C installer --strip-components=1
fi
mkdir -p "$HARBOR_DATA"
envsubst < harbor.yml.tpl > installer/harbor.yml
cd installer
# `prepare` renders installer/common/config/* + docker-compose.yml. It runs as
# root (inside a container) and writes 0600 files, which `docker compose` -
# running as YOU, without sudo - cannot read. install.sh assumes root; we
# run its two steps ourselves and relax the permissions (lab trade-off: the
# rendered secrets become readable by local users).
./prepare
docker run --rm -v "$PWD/common:/c" busybox:1.37 chmod -R a+rX /c
docker compose up -d
cd ..

echo "waiting for Harbor API..."
until curl -sf "http://$LXC_IP:8085/api/v2.0/health" | grep -q '"status":"healthy"'; do sleep 3; done
echo "Harbor UI: http://$LXC_IP:8085  (admin / \$HARBOR_ADMIN_PASSWORD)"
