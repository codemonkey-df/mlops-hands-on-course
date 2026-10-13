#!/usr/bin/env bash
# Skip ahead: copy the verified reference files of a module into your working
# tree and run its deploy script. Your existing files are backed up first.
#   scripts/catchup.sh m03
set -euo pipefail

module="${1:?usage: catchup.sh mNN}"
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

if [[ -x "$ref/_deploy.sh" ]]; then
  echo "running $module deploy..."
  (cd "$root" && "$ref/_deploy.sh")
fi
echo "$module caught up."
