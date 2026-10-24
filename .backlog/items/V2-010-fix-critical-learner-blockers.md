---
id: V2-010
title: Fix critical learner blockers (M1 / M3 / M4)
status: done
track: core
priority: high
effort: M
modules: [M0, M1, M3, M4]
area: docs
depends_on: []
---

# V2-010: Fix critical learner blockers (M1 / M3 / M4)

## Problem

Hands-on lab work (M1 → M5+, `nip.io` + k3d + Safari / local `uv run`)
hits **silent or confusing failures** that look like broken labs:

1. **Platform wiring** — wrong LAN IP / `YOUR_SERVER_IP`, MLflow Host +
   CORS, MinIO Ingress vs cluster IP.
2. **Silent “success” with empty UIs** — MLflow writes to `./mlruns/`
   without `MLFLOW_TRACKING_URI`; Dagster materialize without
   `DAGSTER_HOME` while `dagster dev` uses `.dagster_home`.
3. **Stale lab commands** — guide suggests `kill 1` on Chainguard /
   distroless MinIO (no `kill` / shell).

These must be fixed **before** new v2 features or electives.

Pain themes already partly covered as exercises; gaps are mostly
**missing warnings**, **stale commands**, and **MLflow CORS** not taught
beside allowed-hosts.

## Why it matters for v2

Trust in the course depends on the happy path matching what the docs say.
Platform + docs drift here wastes hours and trains the wrong mental model
(“UI is broken” vs “wrong instance / wrong tab / missing flag”).

## Issues to fix (full detail)

### C1. MLflow Runs tab `INTERNAL_ERROR` (CORS)

| | |
|---|---|
| **Symptom** | Runs tab shows `INTERNAL_ERROR` |
| **Cause** | Missing `--cors-allowed-origins=http://mlflow.<IP>.nip.io:8080`; POST + Origin → 403, UI maps to INTERNAL_ERROR |
| **Fix** | Add CORS flag next to allowed-hosts; keep in platform Deployment; teach in M3 |
| **Where** | `platform/k8s/mlflow/20-deployment.yaml`, `reference/m03/…`, `docs/modules/m03-mlflow.md`, troubleshooting |

### C2. M1 `kubectl exec … -- kill 1` fails on MinIO

| | |
|---|---|
| **Symptom** | `exec: "kill": executable file not found in $PATH` |
| **Cause** | Chainguard/distroless image has no `kill` / shell userland |
| **Fix** | `kubectl -n storage delete pod -l app.kubernetes.io/name=minio` or `rollout restart`; watch EndpointSlices |
| **Where** | `docs/modules/m01-kubernetes-helm.md` (was teaching `kill 1`; fixed) |

### C3. MLflow Overview “Failed to load chart data”

| | |
|---|---|
| **Symptom** | Overview tab fails / empty charts after a successful train |
| **Cause** | MLflow 3 GenAI Overview tabs; classic runs live under **Runs** |
| **Fix** | Tell learners to open **Runs**, not Overview |
| **Where** | `docs/modules/m03-mlflow.md`, troubleshooting |

### C4. Train OK, MLflow UI empty (URI not in process env)

| | |
|---|---|
| **Symptom** | Training succeeds; UI shows no runs |
| **Cause** | `MLFLOW_TRACKING_URI` not in process env → writes to `./mlruns/`. `.env` loaded for S3 via pydantic, **not** for MLflow unless shell sources it |
| **Fix** | Warn asymmetry in docs; optionally load URI in `train.py`; always `set -a && source .env && set +a` |
| **Where** | `docs/modules/m03-mlflow.md`, optional `train.py`, troubleshooting |

### C5. Dagster `/runs` empty after successful materialize

| | |
|---|---|
| **Symptom** | Materialize script prints success; UI `/runs` empty |
| **Cause** | CLI without `DAGSTER_HOME`; UI/`dagster dev` with `.dagster_home` → 0 rows in `runs.db`. (`DagsterHomeNotSetError` on `sensor start` — materialize can use ephemeral instance; sensor cannot.) |
| **Fix** | Document “RUN_SUCCESS but empty UI” + count check; same `DAGSTER_HOME` in every terminal |
| **Where** | `docs/modules/m04-dagster-foundations.md`, troubleshooting |

Related: `Invalid Host header` / DNS rebinding (Safari) from missing /
placeholder `--allowed-hosts` — exercise bug02 exists; still easy to hit
on platform path when `configure-ip` was skipped. Keep CORS +
allowed-hosts taught together.

## Proposed change

1. Add `--cors-allowed-origins=http://mlflow.YOUR_SERVER_IP.nip.io:8080`
   to platform + reference MLflow Deployments; wire into `configure-ip`.
2. Replace MinIO `kill 1` demo with delete/rollout + EndpointSlice watch.
3. Document Runs vs Overview; `.env` / URI asymmetry; Dagster dual-instance
   footgun.
4. Add troubleshooting rows for C1–C5.
5. Ship pre-flight checks (below) into M0/M3/M4 as appropriate.

### Pre-flight / smoke (fold into docs)

```bash
# Shell for every terminal
set -a && source .env && set +a
echo "$MLFLOW_TRACKING_URI"   # non-empty, correct IP
export DAGSTER_HOME=$PWD/.dagster_home && mkdir -p "$DAGSTER_HOME"

# MLflow security flags present
kubectl -n mlflow get deploy mlflow -o yaml | grep -E 'allowed-hosts|cors-allowed'

# CORS smoke (expect 200)
curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Origin: $MLFLOW_TRACKING_URI" \
  -H "Content-Type: application/json" \
  -d '{"experiment_ids":["1"]}' \
  "$MLFLOW_TRACKING_URI/ajax-api/2.0/mlflow/runs/search"

# Dagster instance has runs after materialize
sqlite3 "$DAGSTER_HOME/history/runs.db" "SELECT count(*) FROM runs;"
```

## Acceptance criteria

- [x] Platform + reference MLflow Deployment include CORS flag; survives
      `configure-ip` / IP placeholder substitution
- [x] M1 no longer teaches `exec … kill 1` on MinIO; distroless-safe demo works
- [x] M3 docs: CORS beside allowed-hosts; Runs vs Overview; `.env` / URI asymmetry
- [x] M4 docs: empty-UI / dual-instance failure mode + count check
- [x] Troubleshooting cheatsheet has a row for each of C1–C5
- [x] Manual smoke: train → run visible under Runs; CORS curl returns 200;
      Dagster materialize appears in UI when `DAGSTER_HOME` matches
- [x] `make check-m01` / `check-m03` / `check-m04` (touched) still pass
      (maintainer `make verify-m01` / `verify-m03` / `verify-m04`)

## Out of scope

- High/medium pedagogy polish (IP checklist, pytest scope, Helm `-f`,
  exercise namespaces, MinIO creds callouts, tool map) → **V2-011**
- New features (auto-promote, path personas, electives)

## Notes

**Done before** V2-001 / V2-002 / V2-008 / V2-009 (was a hard prerequisite).

What already works well (do not regress):

- M1 bugs (selector, types, password `lookup`) match real confusion.
- M3 allowed-hosts exercise matches Host-header failures.
- M4 documents `DAGSTER_HOME` (empty-UI dual-instance case covered by this card).
- M5 secrets outside chart + `postgresqlScheme` match production footguns.
- `configure-ip` / nip.io pattern is correct when used consistently.

## Done notes

Branch `fix/V2-010-critical-learner-blockers`. CORS on platform + reference
MLflow; M1 rollout restart; M0/M3/M4 + troubleshooting for C1–C5.
Delivery-only `tests/test_v2_010_platform_guards.py` removed after green (not
course content). Manual: CORS curl 200 + ACAO header; train `logreg-e20` on
Training runs; Dagster `/runs` shows materialize with shared `DAGSTER_HOME`
(sqlite count 7).
