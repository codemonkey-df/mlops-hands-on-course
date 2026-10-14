---
id: V2-003
title: Split Postgres for Dagster + LiteLLM
status: ready
track: core
priority: medium
effort: M
modules: [M1, M5, M9]
area: platform
depends_on: []
---

# V2-003: Split Postgres for Dagster + LiteLLM

## Problem

Postgres is effectively shared / single-purpose in the mental model: MLflow
uses it; Dagster needs durable storage of its own; LiteLLM benefits from a DB
for virtual keys and spend tracking. Crowding one database (or one consumer)
hides real multi-tenant ops concerns.

## Why it matters for v2

Separate databases (same Postgres instance is fine) isolate migrations,
backups, and credential blast radius. LiteLLM without a DB stays ephemeral
for keys/spend — weak for an on-prem “platform” story.

## Proposed change

- Helm/init: create databases + roles, e.g. `mlflow`, `dagster`, `litellm`
  (one StatefulSet / chart, multiple DBs).
- Point Dagster Helm values at `dagster` DB (confirm M5 reference).
- Point LiteLLM at `litellm` DB; document keys/spend UI or API check.
- Secrets: one Secret per consumer (or clearly namespaced keys).
- Docs: M1 “databases vs instances”; M5/M9 connection snippets.
- Exercise: wrong DB name / driver → familiar connect failure
  (extend or mirror existing pg bugs).

## Acceptance criteria

- [ ] Three logical databases exist after Postgres install/upgrade
- [ ] MLflow, Dagster, and LiteLLM each use their own DB credentials
- [ ] LiteLLM persists at least one virtual key or spend row across pod restart
- [ ] Module docs updated; cheatsheet note on “shared instance, split DBs”
- [ ] Relevant `make check-m01` / `check-m05` / `check-m09` pass

## Out of scope

- Separate Postgres instances / HA
- Migrating existing lab data (document wipe + recreate is OK)
- Full LiteLLM SSO / enterprise features

## Notes

Same Postgres pod is enough for the course; the teaching point is **isolation
by database and secret**, not more StatefulSets.

## Done notes

_
