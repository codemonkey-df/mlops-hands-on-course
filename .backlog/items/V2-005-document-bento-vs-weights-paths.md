---
id: V2-005
title: Document Bento vs MinIO weight paths
status: done
track: core
priority: medium
effort: S
modules: [M6, M7, M9, M11]
area: docs
depends_on: []
---

# V2-005: Document Bento vs MinIO weight paths

## Problem

It is unclear who builds/pushes the Bento image (CI vs Dagster) and how the
service gets its model (MLflow vs MinIO). The LLM path uses a MinIO
initContainer for weights; churn serving bakes the model into the image from
MLflow `@champion`. Without an explicit comparison, the two patterns look
like one unfinished design.

## Why it matters for v2

Two valid on-prem patterns (bake-into-image vs pull-at-pod-start). Learners
and future v2 work need a single place that states which path each workload
uses and why.

## Proposed change

- Short “Model delivery paths” callout on home or a cheatsheet page:
  | Workload | Artifact source | Who builds | How cluster gets it |
  | Churn Bento | MLflow `@champion` | CI (import → bento build → Harbor) | Image tag in GitOps |
  | vLLM mock | Fake weights in MinIO | N/A (chart + initContainer) | initContainer copy |
- Cross-link M6 “Releasing a new model”, M7 CI, M9 initContainer, M11 sequence.
- One gotcha: “Dagster does not push serving images.”

## Acceptance criteria

- [x] Table (or equivalent) visible from course home or cheatsheets nav
- [x] M6/M9/M11 each link to it or repeat the one-liner
- [x] No code/platform behaviour change required for this card

## Out of scope

- Unifying both workloads onto one delivery pattern
- Auto promotion → **V2-001**

## Notes

Doc-only; good warm-up card before larger platform work.

## Done notes

Cheatsheet `docs/cheatsheets/model-delivery.md` (nav + home tip); cross-links
M6/M7/M9/M11 + gotchas. Docs-only; merged to `dev` via
`fix/V2-005-document-bento-vs-weights-paths`.
