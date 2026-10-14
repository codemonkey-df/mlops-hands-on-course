# v2 backlog board

Update this table whenever an item’s status or priority changes.

| ID | Title | Status | Priority | Effort | Area | Depends |
|----|-------|--------|----------|--------|------|---------|
| [V2-001](items/V2-001-auto-promotion-loop.md) | Auto promotion loop (registry → GitOps) | ready | high | L | platform | — |
| [V2-002](items/V2-002-ci-model-quality-gate.md) | CI model-quality / eval gate | ready | high | M | ci | — |
| [V2-003](items/V2-003-split-postgres-consumers.md) | Split Postgres for Dagster + LiteLLM | ready | medium | M | platform | — |
| [V2-004](items/V2-004-overview-prom-keda-edge.md) | Overview diagram: prom → KEDA | ready | low | S | docs | — |
| [V2-005](items/V2-005-document-bento-vs-weights-paths.md) | Document Bento vs MinIO weight paths | ready | medium | S | docs | — |

## Suggested order

1. **V2-005** then **V2-004** — cheap clarity wins while finishing the course.
2. **V2-002** — quality gate before automating deploy.
3. **V2-001** — auto loop (builds on a trustworthy gate).
4. **V2-003** — storage isolation (ops hardening; can land anytime).

## How to add

```bash
cp .backlog/TEMPLATE.md .backlog/items/V2-006-my-slug.md
# edit frontmatter + body, then add a row above
```
