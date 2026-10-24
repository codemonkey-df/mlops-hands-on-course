---
id: V2-006
title: Elective — SLURM batch / GPU training path
status: wontfix
track: elective
priority: medium
effort: L
modules: [E-slurm]
area: elective
depends_on: []
---

# V2-006: Elective — SLURM batch / GPU training path

## Problem

The **default v1 path** (Dagster → Kubernetes Jobs → MLflow) is enough for
the core course. Many on-prem sites also use **SLURM** for heavy CPU/GPU
batch work. That is a useful possibility to show — not a reason to make
every student wire SLURM into the main pipeline.

## Why it matters for v2

Offer a **choose-your-path** elective: after (or instead of) the K8s Job
training hop, interested students can build “orchestrator submits → SLURM
schedules → artifacts back to MinIO/MLflow.” Everyone else finishes v1
unchanged.

## Proposed change

- **Do not** change the default training assets, M5 deploy, or M11 happy path.
- Add an **elective module** (e.g. under `docs/electives/slurm/` or `E1`):
  problem → foundations → build → break/fix, same shape as core modules.
- Lab options (pick one when implementing):
  - **A:** small compose SLURM (`slurmctld` + `slurmd`) for real `sbatch`
  - **B:** mock client + scripts so the elective runs without HPC hardware
- Standalone scripts or an **optional** Dagster resource students enable
  only in the elective — not required in default `Definitions`.
- Home / progress page: short “Electives” list — *optional; skip for v1*.
- Reference solution in `reference/electives/…` so catch-up stays optional.

## Acceptance criteria

- [ ] M0–M11 complete without touching this elective
- [ ] Elective docs explain when you’d pick SLURM vs K8s Jobs
- [ ] Student who opts in can submit a job and land an MLflow run / artifact
- [ ] Default Dagster code location does not depend on SLURM
- [ ] New checks (if any) are `make check-e-slurm` (or similar), not forced
      into `check-m05` / `check-m11`

## Out of scope

- Making SLURM the only or default training backend
- Folding SLURM into the M11 capstone as a required hop
- Multi-site federation, accounting, InfiniBand tuning

## Notes

**Superseded by [V2-008](V2-008-ai-systems-engineer-path.md)** (Epic 1 +
Dagster → Slurm + training-on-Slurm). Keeping this file as history only —
do not implement both.

## Done notes

_wontfix — folded into V2-008 (2026-10-24)._
