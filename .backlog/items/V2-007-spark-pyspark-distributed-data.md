---
id: V2-007
title: Elective — Spark (PySpark) distributed data path
status: idea
track: elective
priority: medium
effort: L
modules: [E-spark]
area: elective
depends_on: []
---

# V2-007: Elective — Spark (PySpark) distributed data path

## Problem

The **default v1 path** uses DuckDB/Polars on MinIO — right for lab scale and
for learning the lake. Sites that need **distributed** ETL often use Spark
(Scala engine, Python via PySpark). That is worth offering as a path to
explore, not as a mandatory second engine in every pipeline.

## Why it matters for v2

**Choose-your-path:** students who care about distributed data build an
elective Spark lab against the same MinIO lake. Everyone else keeps the v1
DuckDB path. No dual-engine default workflow.

## Why Spark (PySpark), not raw Scala or Dask

| Option | Role in this elective |
|--------|------------------------|
| **Spark + PySpark (chosen)** | Industry “distributed data” default; Python API; Scala stays under the hood |
| Raw Scala jobs | Optional sidebar only — not required to pass the elective |
| Dask | Plan B if Spark/JVM is too heavy for the lab RAM story |
| Ray | Different goal (distributed train/serve) — separate card if needed |

## Proposed change

- **Do not** replace or require Spark in M2/M4 default assets.
- Add an **elective module** (`docs/electives/spark/` or similar): stand up
  a tiny Spark setup (in-process `local[*]` first, optional workers later)
  and run one read → transform → write against MinIO.
- Teaching goal: *when* DuckDB is enough vs *when* you’d reach for Spark —
  decision, not “always use both.”
- Optional curiosity box: 10 lines of Scala / `spark-shell` — not graded.
- Progress page: listed under Electives; skippable for v1 completion.
- Reference under `reference/electives/…` only.

## Acceptance criteria

- [ ] Completing M0–M11 never requires Spark or extra JVM services
- [ ] Elective student can run a PySpark job R/W on the MinIO lake
- [ ] Docs frame this as an alternative data engine, not a pipeline rewrite
- [ ] Default `dvc.yaml` / Dagster assets unchanged unless learner copies
      elective snippets on purpose
- [ ] Checks (if any) are elective-scoped (`make check-e-spark`), not core

## Out of scope

- Making Spark the default ingest/transform path
- Dual-running DuckDB + Spark in the core daily_ingest job
- Full lakehouse (Iceberg/Delta) or streaming — later electives if useful

## Notes

**Track = elective.** Possibilities students choose and build — not more
mandatory hops.

User ask was “SCALA (or choose which fit).” Answer for the elective:
**Spark/PySpark**; Scala is the engine, not the course language.

Related: **V2-006** = HPC *compute* path; this = *data* path. Independent
opt-ins.

## Done notes

_
