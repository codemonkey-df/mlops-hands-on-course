#!/usr/bin/env bash
# Skip ahead: copy the verified reference files of a module into your working
# tree and run its deploy script. Your existing files are backed up first.
#   scripts/catchup.sh m03               copy files + deploy
#   scripts/catchup.sh m03 --files-only  copy files only
set -euo pipefail

module="${1:?usage: catchup.sh mNN [--files-only]}"
files_only="${2:-}"
root="$(cd "$(dirname "$0")/.." && pwd)"
ref="$root/reference/$module"
[[ -d "$ref" ]] || { echo "no reference for $module"; exit 1; }

backup="$root/.catchup-backup/$module-$(date +%Y%m%d-%H%M%S)"
cd "$ref"
find . -type f ! -name '_deploy.sh' | while read -r f; do
  target="$root/${f#./}"
  if [[ -f "$target" ]] && ! cmp -s "$f" "$target"; then
    mkdir -p "$backup/$(dirname "${f#./}")"
    cp "$target" "$backup/${f#./}"
  fi
  mkdir -p "$(dirname "$target")"
  cp "$f" "$target"
done
[[ -d "$backup" ]] && echo "your previous versions were saved in $backup"

if [[ -x "$ref/_deploy.sh" && "$files_only" != "--files-only" ]]; then
  echo "running $module deploy..."
  (cd "$root" && "$ref/_deploy.sh")
fi
# Reference files use YOUR_SERVER_IP; rewrite to this machine's LAN IP.
if grep -Rql 'YOUR_SERVER_IP' "$root/platform" "$root/src" 2>/dev/null; then
  echo "rewriting YOUR_SERVER_IP -> SERVER_IP..."
  (cd "$root" && "$root/scripts/configure-ip.sh")
fi
echo "$module caught up."
