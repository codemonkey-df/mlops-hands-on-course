---
id: V2-004
title: Overview diagram: prom → KEDA
status: done
track: core
priority: low
effort: S
modules: [M10]
area: docs
depends_on: []
---

# V2-004: Overview diagram: prom → KEDA

## Problem

The home architecture diagram (`docs/index.md`) shows KEDA next to vLLM but
no edge from Prometheus. Learners infer KEDA has “no visible trigger.” M10’s
own diagram already has `prom → keda`; the overview is incomplete.

## Why it matters for v2

The first diagram is how people form the platform mental model. Missing the
metrics → scaler link makes KEDA look decorative.

## Proposed change

- Update `docs/index.md` mermaid: `prom --> keda` (and keep `keda --> vllm`).
- Optionally add a one-line caption: “KEDA scales on PromQL (see M10).”
- Mirror the same edge in any cheatsheet / architecture dump if duplicated.

## Acceptance criteria

- [x] Home diagram includes Prometheus → KEDA → workload
- [x] Wording does not contradict M10 (`metricType: Value`, min replicas)
- [x] Site builds (`make docs` / mkdocs) with valid mermaid

## Out of scope

- New ScaledObjects or metrics
- Scaling Bento (only document if already true)

## Notes

Pure docs; safe to do anytime, including mid-course.

## Done notes

Merged to `dev`: home mermaid adds `prom --> keda` (kept `keda --> vllm`) plus
one-line PromQL caption linking to M10. No platform/YAML changes.

