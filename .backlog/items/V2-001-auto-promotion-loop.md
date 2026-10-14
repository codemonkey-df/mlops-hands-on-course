---
id: V2-001
title: Auto promotion loop (registry → GitOps)
status: ready
priority: high
effort: L
modules: [M7, M8, M11]
area: platform
depends_on: [V2-002]
---

# V2-001: Auto promotion loop (registry → GitOps)

## Problem

Training writes to MLflow and MinIO, and Dagster can move `@champion`, but
deployment still needs a human `workflow_dispatch` in Gitea. Registry promotion
and serving are disconnected unless someone remembers to run CI. The only
“automatic” weight path today is the LLM MinIO initContainer — a different
pattern.

## Why it matters for v2

A real platform should make “new champion → new serving revision” a closed
loop (or an explicit, auditable exception). M11 teaches the manual hop on
purpose; v2 should show the automated GitOps path without losing rollback via
Git.

## Proposed change

- Trigger CI (or a small release job) when `@champion` changes — e.g. Dagster
  sensor / asset hook, MLflow webhook, or a poll job that compares alias →
  last baked version.
- Job: import `@champion` → build/push Bento → commit image tag under
  `platform/gitops/` (same `# ci:churn-tag` contract as today).
- Keep ArgoCD as the only cluster mutator; no `kubectl set image` from CI.
- Update M11: “auto path” as default tweak; keep one exercise where auto is
  off so learners still see registry ≠ serving.
- Document failure modes: promote-but-CI-red, CI-but-wrong-gitops-path,
  ArgoCD OutOfSync.

## Acceptance criteria

- [ ] Champion alias change eventually results in a Git commit bumping the
      serving image tag (no manual Actions click required in the happy path)
- [ ] ArgoCD rolls serving; `/model_info` matches new MLflow version
- [ ] Rollback remains `git revert` + ArgoCD sync
- [ ] Capstone / docs explain auto vs intentional manual hold
- [ ] `[skip ci]` / `paths-ignore` still prevent tag-bump loops
- [ ] Touched `make check-m07` / `check-m08` / `check-m11` pass

## Out of scope

- Multi-env promote (staging → prod) — separate card if needed
- Canary / traffic splitting
- Quality gate logic itself → **V2-002** (should land first or with this)

## Notes

Course today (M11): Dagster → `@champion` → human CI → Harbor → gitops →
ArgoCD. Preserve that mental model; automation is an extra hop, not a
replacement for Git as source of truth.

## Done notes

_
