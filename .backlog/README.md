# Course v2 backlog

One item = one shippable change to the course (docs, reference code, exercises,
or platform). Pick the next `ready` card, implement it, mark it `done`, then
take another.

## Layout

```text
.backlog/
  README.md           # this file
  TEMPLATE.md         # copy → items/V2-NNN-slug.md
  INDEX.md            # status board (keep in sync)
  items/              # one markdown file per feature/change
```

## Workflow

1. **Add** — copy `TEMPLATE.md` to `items/V2-NNN-short-slug.md`, fill every
   section, add a row to `INDEX.md`.
2. **Pick** — choose one `ready` item (prefer higher priority / lower effort).
3. **Do** — set `status: in-progress` in the item and in `INDEX.md`. Change
   only what the card’s acceptance criteria require.
4. **Done** — set `status: done`, fill **Done notes** (PR / commit / modules
   touched). Leave the file in place as history.

Statuses: `idea` → `ready` → `in-progress` → `done` | `wontfix`

## Naming

`V2-NNN-kebab-slug.md` — next free number, lowercase slug, no spaces.

## Scope of a good card

- Fits in one focused PR / work session when possible
- Names which modules / paths change (`docs/`, `reference/`, `platform/`, …)
- Has testable acceptance criteria
- Does **not** bundle unrelated gaps (split instead)
