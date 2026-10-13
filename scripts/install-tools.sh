#!/usr/bin/env bash
# Install the course CLIs into ~/.local/bin (no sudo needed).
# Versions are pinned so every module behaves the same way it did when written.
set -euo pipefail

KUBECTL_VERSION="v1.37.1"   # client may be +-1 minor of the server (k3s 1.35 -> fine)
K3D_VERSION="v5.9.0"
HELM_VERSION="v4.3.0"       # Helm 4! Most tutorials online still show Helm 3 (see gotchas)
K9S_VERSION="v0.51.0"
DVC_VERSION="3.67.1"

BIN="$HOME/.local/bin"
mkdir -p "$BIN"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

echo "kubectl $KUBECTL_VERSION"
curl -fsSLo "$BIN/kubectl" "https://dl.k8s.io/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl"
chmod +x "$BIN/kubectl"

echo "k3d $K3D_VERSION"
curl -fsSLo "$BIN/k3d" "https://github.com/k3d-io/k3d/releases/download/$K3D_VERSION/k3d-linux-amd64"
chmod +x "$BIN/k3d"

echo "helm $HELM_VERSION"
curl -fsSL "https://get.helm.sh/helm-$HELM_VERSION-linux-amd64.tar.gz" | tar xz -C "$tmp"
mv "$tmp/linux-amd64/helm" "$BIN/helm"

echo "k9s $K9S_VERSION"
curl -fsSL "https://github.com/derailed/k9s/releases/download/$K9S_VERSION/k9s_Linux_amd64.tar.gz" \
  | tar xz -C "$BIN" k9s

echo "dvc $DVC_VERSION (isolated uv tool, with the S3 remote plugin)"
uv tool install --force "dvc[s3]==$DVC_VERSION"

echo; echo "Installed:"
kubectl version --client | head -1
k3d version | head -1
helm version --short
k9s version --short | head -1
dvc --version
