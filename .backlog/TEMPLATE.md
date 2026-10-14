---
id: V2-NNN
title: Short imperative title
status: idea          # idea | ready | in-progress | done | wontfix
track: core           # core = harden v1 path | elective = optional path students choose
priority: medium      # high | medium | low
effort: M             # S (~half day) | M (~1–2 days) | L (multi-day)
modules: []           # e.g. [M7, M8, M11] or [E1] for electives
area: platform        # docs | platform | pipelines | ci | exercises | infra | elective
depends_on: []        # e.g. [V2-001]
---

# V2-NNN: Short imperative title

## Problem

What is wrong or missing today (learner or platform perspective)?

## Why it matters for v2

One or two sentences: production realism, teaching clarity, or ops safety.

## Proposed change

Concrete work — files, components, behaviours. Prefer bullets.

- For **elective** cards: describe an opt-in module/lab. Do **not** require
  changing the default v1 pipeline.

## Acceptance criteria

- [ ] …
- [ ] …
- [ ] Docs / cheatsheet updated if behaviour changes
- [ ] `make check-mNN` (or listed checks) still pass for touched modules
- [ ] *(elective)* Completing M0–M11 without this path still works unchanged

## Out of scope

What this card explicitly does **not** include (park as another item).

## Notes

Links, prior discussion, gotchas.

## Done notes

_Filled when status → done: commit SHA / PR, date, anything follow-up._
