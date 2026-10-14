# Course v2 backlog

One item = one shippable change. Pick a `ready` card, implement it, mark it
`done`, then take another.

## Two kinds of card

| Track | Purpose | Rule |
|-------|---------|------|
| **core** | Close gaps in the existing M0–M11 path | May change platform/CI/docs; v1 still works end-to-end |
| **elective** | Optional learning path a student can *choose* | Must **not** rewrite the default pipeline; v1 path stays the main line |

Electives show **possibilities** (SLURM, Spark, …): a short module or lab a
curious student builds *instead of or after* the default hop — not another
mandatory hop bolted onto every run.

## Layout

```text
.backlog/
  README.md           # this file
  TEMPLATE.md         # copy → items/V2-NNN-slug.md
  INDEX.md            # status board (keep in sync)
  items/              # one markdown file per feature/change
```

## Workflow

1. **Add** — copy `TEMPLATE.md` to `items/V2-NNN-short-slug.md`, set
   `track: core` or `track: elective`, add a row to `INDEX.md`.
2. **Pick** — choose one `ready` item (prefer higher priority / lower effort).
3. **Do** — set `status: in-progress` in the item and in `INDEX.md`.
4. **Done** — set `status: done`, fill **Done notes**. Leave the file as history.

Statuses: `idea` → `ready` → `in-progress` → `done` | `wontfix`

## Naming

`V2-NNN-kebab-slug.md` — next free number, lowercase slug, no spaces.

## Scope of a good card

- Fits in one focused PR / work session when possible
- Names which modules / paths change (`docs/`, `reference/`, `platform/`, …)
- Has testable acceptance criteria
- Does **not** bundle unrelated gaps (split instead)
- **Elective:** default M0–M11 behaviour unchanged unless the learner opts in
