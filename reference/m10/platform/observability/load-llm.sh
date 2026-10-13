#!/usr/bin/env bash
# Fill the small-chat queue so Grafana and KEDA have something to show.
# Concurrency >> maxNumSeqs (8) is what produces vllm:num_requests_waiting.
#
#   platform/observability/load-llm.sh [N] [CONCURRENCY]
set -euo pipefail
N="${1:-200}"
CONC="${2:-64}"
echo "sending $N tickets at concurrency $CONC (small-chat maxNumSeqs=8, so the rest WAIT)"
exec platform/llm/run-tickets.sh "$N" "$CONC"
