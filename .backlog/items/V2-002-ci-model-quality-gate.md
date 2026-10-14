---
id: V2-002
title: CI model-quality / eval gate
status: ready
priority: high
effort: M
modules: [M7, M11]
area: ci
depends_on: []
---

# V2-002: CI model-quality / eval gate

## Problem

CI is thin for promotion: lint/tests/image build exist, but there is no
blocking eval or model-quality check before a new Bento tag is pushed and
written into GitOps. Dagster’s champion/challenger compare is the only gate,
and it lives outside the release pipeline.

## Why it matters for v2

Images and manifests should not advance on “CI green for packaging” alone.
A second, release-time gate (holdout metrics, schema/signature check, smoke
predict) catches “champion in registry, broken in the image” failures.

## Proposed change

- Add a CI job (before push / gitops commit) that:
  - loads the candidate from MLflow `@champion` (or the version about to bake)
  - runs a fixed eval set (synthetic holdout in MinIO or repo fixture)
  - fails the workflow if metrics fall below thresholds in `params.yaml`
    (or a small `eval.yaml`)
- Optional: signature / input-schema smoke (`predict` on one valid + one
  invalid row) so Bento packaging bugs fail before Harbor.
- Wire thresholds into course docs (M7 foundations + M11 “gate failed”
  tweak).
- Exercise: plant a failing threshold or broken signature; `make check`
  expects red CI / job failure.

## Acceptance criteria

- [ ] Release path cannot push a serving tag if eval gate fails
- [ ] Thresholds are config, not hardcoded in the workflow script
- [ ] At least one unit/integration test covers the eval helper offline
- [ ] Docs state: Dagster promote gate vs CI release gate (both exist)
- [ ] `make check-m07` (and any new m11 gate exercise) pass

## Out of scope

- Full shadow traffic / online A/B
- Auto-rollback on Grafana drift (observability card later)
- Auto promotion trigger → **V2-001**

## Notes

Prefer reusing training metrics code under `src/mlops_course/` so CI and
Dagster do not diverge. Keep the eval set tiny for lab runtime.

## Done notes

_
