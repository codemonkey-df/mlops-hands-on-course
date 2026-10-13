#!/usr/bin/env bash
# Replace the course placeholder YOUR_SERVER_IP with this machine's LAN IP.
# Run once after clone (and again if your IP changes):
#   make configure-ip
#   # or: SERVER_IP=10.0.0.5 make configure-ip
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

SERVER_IP="${SERVER_IP:-$(hostname -I | awk '{print $1}')}"
if [[ -z "$SERVER_IP" || "$SERVER_IP" == "YOUR_SERVER_IP" ]]; then
  echo "Could not detect SERVER_IP. Set it explicitly:"
  echo "  SERVER_IP=192.168.x.y make configure-ip"
  exit 1
fi

# Runtime / learner tree only — leave docs/ and most of reference/ as the
# placeholder so the course text stays generic. Catch-up copies reference
# into platform/; re-run this script after catchup if needed.
paths=(
  platform
  src
  infra
  .dvc
  .env.example
  exercises
)
[[ -f .env ]] && paths+=(.env)

n=0
for path in "${paths[@]}"; do
  [[ -e "$path" ]] || continue
  while IFS= read -r -d '' f; do
    if grep -q 'YOUR_SERVER_IP' "$f" 2>/dev/null; then
      sed -i "s/YOUR_SERVER_IP/${SERVER_IP}/g" "$f"
      n=$((n + 1))
      echo "  updated $f"
    fi
  done < <(find "$path" -type f \( \
    -name '*.yaml' -o -name '*.yml' -o -name '*.tpl' -o -name '*.py' \
    -o -name '*.sh' -o -name '*.md' -o -name '*.txt' -o -name '*.json' \
    -o -name 'config' -o -name '.env' -o -name '.env.example' \
  \) ! -path '*/.git/*' -print0)
done

echo
echo "SERVER_IP=$SERVER_IP  ($n files updated)"
echo "UIs will look like:  http://grafana.${SERVER_IP}.nip.io:8080"
echo "Next: copy .env.example -> .env if you have not already, then make cluster-up / make docs"
