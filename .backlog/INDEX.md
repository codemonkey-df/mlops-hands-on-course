# v2 backlog board

Update this table whenever an item’s status or priority changes.

**Tracks:** `core` = harden / clarify the existing course · `elective` =
optional path (show a possibility; do not overbuild the default workflow).

## Core (v1 path)

| ID | Title | Status | Priority | Effort | Area | Depends |
|----|-------|--------|----------|--------|------|---------|
| [V2-001](items/V2-001-auto-promotion-loop.md) | Auto promotion loop (registry → GitOps) | ready | high | L | platform | — |
| [V2-002](items/V2-002-ci-model-quality-gate.md) | CI model-quality / eval gate | ready | high | M | ci | — |
| [V2-003](items/V2-003-split-postgres-consumers.md) | Split Postgres for Dagster + LiteLLM | ready | medium | M | platform | — |
| [V2-004](items/V2-004-overview-prom-keda-edge.md) | Overview diagram: prom → KEDA | ready | low | S | docs | — |
| [V2-005](items/V2-005-document-bento-vs-weights-paths.md) | Document Bento vs MinIO weight paths | ready | medium | S | docs | — |

## Electives (choose & build)

Optional labs/modules. Default remains Dagster → K8s Jobs, DuckDB/Polars,
manual/CI promote. Students who want HPC batch or distributed data pick one
of these instead of (or after) the matching v1 hop.

| ID | Title | Status | Priority | Effort | Area | Depends |
|----|-------|--------|----------|--------|------|---------|
| [V2-006](items/V2-006-slurm-batch-training.md) | Elective: SLURM batch / GPU training path | idea | medium | L | elective | — |
| [V2-007](items/V2-007-spark-pyspark-distributed-data.md) | Elective: Spark (PySpark) data path | idea | medium | L | elective | — |

## Suggested order

1. **V2-005** then **V2-004** — cheap clarity wins while finishing the course.
2. **V2-002** — quality gate before automating deploy.
3. **V2-001** — auto loop (builds on a trustworthy gate).
4. **V2-003** — storage isolation (ops hardening; can land anytime).
5. **Electives (V2-006 / V2-007)** — after core; ship as opt-in modules, not
   pipeline rewrites. Flip `idea` → `ready` once the “choose your path”
   framing is sketched in docs.

## How to add

```bash
cp .backlog/TEMPLATE.md .backlog/items/V2-008-my-slug.md
# set track: core | elective, then add a row in the matching table
```
