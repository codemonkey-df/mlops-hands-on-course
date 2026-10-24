---
id: V2-011
title: Fix high learner friction (docs / pedagogy, M0–M5)
status: ready
track: core
priority: high
effort: M
modules: [M0, M1, M2, M5]
area: docs
depends_on: [V2-010]
---

# V2-011: Fix high learner friction (docs / pedagogy, M0–M5)

## Problem

After Critical blockers (**V2-010**), the same hands-on course run still
leaves High and Medium friction: IP drift across Ingress/CORS/`.env`,
bare `pytest` on an incomplete Path A tree, editable-install import
failures, unclear exercise namespaces, Helm “where do overrides get
installed?”, and several M1/M5 pedagogy gaps.

Environment context: `nip.io` + k3d + Safari / local `uv run`.

## Why it matters for v2

These are the next wall learners hit once CORS/UI/instance bugs are
fixed. Closing them keeps M0–M5 self-serve before path choosers or
electives.

## Issues to fix (full detail)

### High

#### H1. Single-IP checklist after any IP change

| | |
|---|---|
| **Symptom** | `http://minio.192.168.1.201.nip.io:8080` fails; curl exit 6 / empty `SERVER_IP`; MLflow Host/CORS mismatch |
| **Cause** | Cluster/`configure-ip` used one IP (e.g. 202); Ingress or browser used another (201); or `$SERVER_IP` unset |
| **Fix** | `hostname -I`, `make configure-ip`, re-apply Ingress; curl with `Host:` against `127.0.0.1:8080` to prove Traefik |
| **Course gap** | Stronger “one IP everywhere” checklist: `configure-ip`, Ingress, allowed-hosts, CORS, `.env` |

#### H2. Don’t run full `pytest` on Path A mid-course

| | |
|---|---|
| **Symptom** | `uv run pytest` ImportError for `training`, `pipelines`, `serving`, … while only `data` exists |
| **Cause** | Repo `tests/` covers all modules; Path A tree incomplete until catch-up/implement |
| **Fix** | `uv run pytest -q tests/test_data_generator.py` (or module-specific); `make catchup-mNN` when needed |
| **Course gap** | README/M2: “don’t run bare `pytest` until catch-up; use the test file for the current module” |

#### H3. `No module named 'mlops_course'` with `uv run python`

| | |
|---|---|
| **Cause** | Broken/empty editable install; pytest works via `pythonpath = ["src"]`, plain `uv run python` does not |
| **Fix** | `uv sync --reinstall-package mlops-course`; or `PYTHONPATH=src` workaround |
| **Course gap** | Troubleshooting row; ensure `__init__.py` / package layout in early steps |

#### H4. Exercise namespaces not named (`<ns>` for `make check-m01`)

| | |
|---|---|
| **Cause** | Pattern `ex-m01-bugNN` only while check runs (then deleted) |
| **Course gap** | State namespace explicitly in each bug intro: “for bug01 use `-n ex-m01-bug01`” |

#### H5. Helm: “overrides in `helm-values/`” but no separate install step

| | |
|---|---|
| **Confusion** | `_helpers.tpl` / `include`; `lookup` + password; where overrides are “installed” |
| **Clarification** | `-f platform/helm-values/postgres.yaml` **on** `helm upgrade --install` *is* the install; helpers DRY labels/names; `lookup` avoids rotating passwords on upgrade |
| **Course gap** | One sentence next to first `helm upgrade`: “You never install the overrides file alone; you always pass `-f`.” |

### Medium

#### M1a. MinIO console login + buckets unclear

| | |
|---|---|
| **Symptom** | Unclear how to log into console; buckets already present (`dvc`, `mlflow`, …) |
| **Cause** | Creds in `platform/k8s/storage/10-minio-secret.yaml`; buckets from Job `60-minio-buckets-job.yaml` (`mc mb …`) |
| **Course gap** | Explicit “console login = Secret keys” + “buckets Job creates X” near health-check |

#### M1b. `kubectl get pods -w` shows nothing after deleting MinIO

| | |
|---|---|
| **Cause** | Watch without `-n storage` (default ns); or recreate finished before watch started |
| **Fix** | `kubectl -n storage get pods -w` in one terminal, then delete |
| **Course gap** | Always show `-n storage` in watch examples next to delete |

#### M1c. MinIO CrashLoop / buckets Job failing (debug order)

| | |
|---|---|
| **Symptom** | `minio` Running → Error quickly; `minio-buckets` retries / fails |
| **Cause** | Buckets Job depends on healthy MinIO. Startup exit often: short `MINIO_ROOT_PASSWORD` (< 8), bad Secret keys, or volume/`runAsUser` for Chainguard uid |
| **Fix** | Fix MinIO first (`logs --previous`); ignore buckets until MinIO is Ready |
| **Course gap** | Callout: “debug order: MinIO before Job” |

#### M1d. Service selector vs pod labels (bug01 pedagogy)

| | |
|---|---|
| **Symptom** | Pod Running but curl times out; “valid YAML, no endpoints” |
| **Cause** | Service `selector: {app: minio}` ≠ pod `app.kubernetes.io/name: minio` |
| **Course gap** | Before exercises: 3-line diagram Pod labels → Service selector → Endpoints; show `kubectl get endpoints` as smoking gun |

#### M1e. Why `| quote` / what is `17.10` in YAML? (bug05)

| | |
|---|---|
| **Cause** | Unquoted numbers → API type error; `17.10` may become float `17.1` |
| **Course gap** | Hint line: “`helm template` succeeds; `kubectl apply` fails on types” |

#### M1f. bug06 password rotates every upgrade

| | |
|---|---|
| **Cause** | `randAlphaNum` without `lookup` reuse |
| **Note** | Exercise is good; tie it to the platform Postgres Secret template for transfer |

#### M2. DuckDB REPL indent error when pasting multi-line `with`

| | |
|---|---|
| **Cause** | Mixed spaces in pasted block — not S3/DuckDB |
| **Course gap** | Optional: ship a tiny script instead of only REPL paste for the health query |

#### M5. Helm Dagster overrides confusion

- Official values are **external** (`helm show values dagster/dagster`);
  repo only has overrides.
- `global.postgresqlSecretName` vs top-level
  `generatePostgresqlPasswordSecret` — same idea, different nesting
  (chart schema).
- Repeating chart defaults (`enabled: true`) in `-f` file is optional.
- How to choose overrides: needs → search defaults → smallest `-f` →
  `helm template` / `helm get values --all`.

**Course gap:** short “overrides vs defaults” box in M5.

#### Ops / concepts

- MLflow pod ~96% MEM: clarify **% of request vs limit**; near limit →
  OOM risk.
- `kubectl get pods -A` for all namespaces.
- Optional one-page **tool map**:

  | Question | Short answer |
  |----------|----------------|
  | dlt used here? | No |
  | DuckDB vs Postgres? | Analytics over Parquet vs platform metadata |
  | BentoML vs Harbor? | Serve/package model vs store images |
  | BentoML vs LLM proxy? | Custom model service vs gateway to many LLMs |
  | KServe for small always-on vLLM? | Often overkill |
  | Slurm in MLOps? | Train/batch GPU farm; serve still k8s/etc. |

### Pre-flight extras (with V2-010)

```bash
# Identity after IP settle
hostname -I | awk '{print $1}'
# SERVER_IP=x.x.x.x make configure-ip

# Package import
uv run python -c "import mlops_course; print(mlops_course.__file__)"

# MinIO / storage watch (correct namespace)
kubectl -n storage get pods -w
```

## Proposed change

- Document H1–H5 and Medium items above in the named modules +
  `docs/cheatsheets/troubleshooting.md`.
- Prefer small callouts and checklist boxes over long new chapters.
- Tool map can be a stub that later links electives (**V2-007** / **V2-008**).

## Acceptance criteria

- [ ] Single-IP checklist exists and is linked from M0 / M1 / M3
- [ ] Path A pytest guidance in README or M2; editable-install row in
      troubleshooting
- [ ] M1 exercises name namespaces; Endpoints tip before bug01; bug05
      template-vs-apply hint; MinIO-before-Job + creds/buckets at health-check
- [ ] Watch examples use `-n storage`
- [ ] Helm `-f` wording in M1; M5 override methodology box
- [ ] Optional tool map stub (or explicitly deferred in Done notes)
- [ ] Docs-only: no default pipeline behaviour change
- [ ] Touched `make check-m01` / `check-m02` / `check-m05` still pass

## Out of scope

- Critical CORS / kill / Runs / URI / DAGSTER_HOME → **V2-010** (do first)
- Role-based paths → **V2-009**
- Elective labs → **V2-007** / **V2-008**

## Notes

Depends on **V2-010**. This card is self-contained — no external gaps
file required.

## Done notes

_
