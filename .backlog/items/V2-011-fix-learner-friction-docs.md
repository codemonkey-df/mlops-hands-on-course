---
id: V2-011
title: Fix high learner friction (docs / pedagogy, M0–M5)
status: done
track: core
priority: high
effort: M
modules: [M0, M1, M2, M3, M5]
area: docs
depends_on: [V2-010]
---

# V2-011: Fix high learner friction (docs / pedagogy, M0–M5)

## Problem

After Critical blockers (**V2-010**), the same hands-on course run still
left High and Medium friction: IP drift across Ingress/CORS/`.env`, bare
`pytest` on an incomplete Path A tree, editable-install import failures,
unclear exercise namespaces, Helm “where do overrides get installed?”,
and several M1/M5 pedagogy gaps.

## Why it matters for v2

These were the next wall learners hit once CORS/UI/instance bugs were
fixed. Closing them keeps M0–M5 self-serve before path choosers or
electives.

## Acceptance criteria

- [x] Single-IP checklist exists and is linked from M0 / M1 / M3
- [x] Path A pytest guidance in README or M2; editable-install row in
      troubleshooting
- [x] M1 exercises name namespaces; Endpoints tip before bug01; bug05
      template-vs-apply hint; MinIO-before-Job + creds/buckets at health-check
- [x] Watch examples use `-n storage`
- [x] Helm `-f` wording in M1; M5 override methodology box
- [x] Optional tool map stub (or explicitly deferred in Done notes)
- [x] Docs-only: no default pipeline behaviour change
- [x] Touched `make check-m01` / `check-m02` / `check-m05` still pass
      (docs-only; exercises unchanged)

## Out of scope

- Critical CORS / kill / Runs / URI / DAGSTER_HOME → **V2-010**
- Role-based paths → **V2-009**
- Elective labs → **V2-007** / **V2-008**

## Done notes

Branch `fix/V2-011-learner-friction-docs`. Shipped callouts/checklists in
M0 (One IP everywhere), M1 (creds/buckets, MinIO-before-Job, `-n storage`
watch, namespaces, Endpoints diagram, helm `-f`, bug05/bug06 hints), M2
(module-scoped pytest + `reference/m02/scripts/duckdb_lake_health.py`),
M3 (IP link), M5 (overrides vs defaults), README Path A,
`troubleshooting.md` (IP + editable install + MEM%),
`docs/cheatsheets/tool-map.md` + mkdocs nav. Issues detail removed from
this card after ship. Delivery-only `tests/test_v2_011_docs.py` removed
before merge. Manual: MkDocs M0/M1/M2/M5 + tool-map; Host curl MinIO 200;
`import mlops_course` OK. Docs-only — `check-m01`/`m02`/`m05` exercises
unchanged.
