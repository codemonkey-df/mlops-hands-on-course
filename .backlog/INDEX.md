# v2 backlog board

Update this table whenever an item’s status or priority changes.

**Tracks:** `core` = harden / clarify the existing course · `elective` =
optional path (show a possibility; do not overbuild the default workflow).

**Rule:** fix learner blockers (**V2-010**, **V2-011**) **before** new
features or electives.

## Core (v1 path)

| ID | Title | Status | Priority | Effort | Area | Depends |
|----|-------|--------|----------|--------|------|---------|
| [V2-010](items/V2-010-fix-critical-learner-blockers.md) | Fix critical learner blockers (M1 / M3 / M4) | done | high | M | docs | — |
| [V2-011](items/V2-011-fix-learner-friction-docs.md) | Fix high learner friction (docs / pedagogy, M0–M5) | ready | high | M | docs | V2-010 |
| [V2-005](items/V2-005-document-bento-vs-weights-paths.md) | Document Bento vs MinIO weight paths | ready | medium | S | docs | — |
| [V2-004](items/V2-004-overview-prom-keda-edge.md) | Overview diagram: prom → KEDA | ready | low | S | docs | — |
| [V2-009](items/V2-009-role-based-learning-paths.md) | Role-based learning paths (starter questions + personas) | ready | high | M | docs | — |
| [V2-002](items/V2-002-ci-model-quality-gate.md) | CI model-quality / eval gate | ready | high | M | ci | — |
| [V2-001](items/V2-001-auto-promotion-loop.md) | Auto promotion loop (registry → GitOps) | ready | high | L | platform | V2-002 |
| [V2-003](items/V2-003-split-postgres-consumers.md) | Split Postgres for Dagster + LiteLLM | ready | medium | M | platform | — |

## Electives (choose & build)

Optional labs/modules. Default remains Dagster → K8s Jobs, DuckDB/Polars,
manual/CI promote. Students who want HPC / systems depth or distributed
data pick one of these instead of (or after) the matching v1 hop — guided
by **V2-009** personas / starter questions.

| ID | Title | Status | Priority | Effort | Area | Depends |
|----|-------|--------|----------|--------|------|---------|
| [V2-008](items/V2-008-ai-systems-engineer-path.md) | Elective: AI systems engineer path (Slurm → eval → train → data) | ready | high | L | elective | V2-009 |
| [V2-007](items/V2-007-spark-pyspark-distributed-data.md) | Elective: Spark (PySpark) data path | idea | medium | L | elective | — |

## Closed / wontfix

| ID | Title | Status | Note |
|----|-------|--------|------|
| [V2-006](items/V2-006-slurm-batch-training.md) | Elective: SLURM batch / GPU training path | wontfix | Superseded by V2-008 Epic 1 |

## Suggested order

1. **V2-010** — critical blockers (CORS, MinIO `kill`, MLflow Runs/URI,
   Dagster empty UI). **Do first.**
2. **V2-011** — remaining High/Medium docs/pedagogy friction.
3. **V2-005** then **V2-004** — cheap clarity wins.
4. **V2-009** — path chooser (personas + starter questions).
5. **V2-002** — quality gate before automating deploy.
6. **V2-001** — auto loop (builds on a trustworthy gate).
7. **V2-003** — storage isolation (ops hardening; can land anytime).
8. **V2-008** — AI Systems Engineer elective (after happy path is solid).
9. **V2-007** — optional Spark data path.

## How to add

```bash
cp .backlog/TEMPLATE.md .backlog/items/V2-012-my-slug.md
# set track: core | elective, then add a row in the matching table
```
