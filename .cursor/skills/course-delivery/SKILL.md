---
name: course-delivery
description: >-
  Applies the fixed mlops-dev backlog delivery workflow when the user provides
  a backlog item (V2-0xx, .backlog/items/). Branch from dev; Planner then
  Reviewer then Builder; Plan → TDD build → findings-only multi-lens review
  (max 3 cycles) → tests → learner browser walkthrough → merge to dev only.
  Use when the user names a backlog ID, attaches a backlog card, says implement
  backlog, merge to dev, or asks to deliver a course fix without restating process.
---

# Course delivery

User supplies a backlog item. Run this workflow. Do not ask them to restate Plan / Review / Build / Manual rules.

```text
User: "Do V2-010"  (or @.backlog/items/V2-010-….md)
Agent: this skill → fixed phases on that item only
```

**Input:** backlog ID or file under `.backlog/items/`
**Output:** item Done + branch merged to `dev` when gates pass
**Announce** the active role at every phase switch: `Role: Planner` | `Role: Reviewer` | `Role: Builder`

Checklists and finding templates: [reference.md](reference.md)

## 1. Git

- Branch from `dev`: `git checkout dev && git pull && git checkout -b fix/V2-0xx-slug` (or `feat/…`).
- Merge / PR **into `dev` only**.
- **Never** merge to `main` in this flow. `main` is release-only, out of band.
- Commit and merge **only after** Tests and Manual pass.

## 2. Backlog entry

1. Resolve the named ID to `.backlog/items/<id>-*.md`.
2. If no item named: read `.backlog/INDEX.md` Suggested order and ask which ID — do not pick silently unless they said “next” / “first ready”.
3. If the named item skips an open higher-priority blocker: warn once; proceed only if they confirm.
4. That card’s **Acceptance criteria** = definition of done. Respect **Out of scope**. Update status / Done notes when finished.

## 3. Roles

Same agent may switch hats. Obey the active role.

| Role | May | Must not |
|------|-----|----------|
| **Planner** | Read backlog + codebase; CreatePlan / edit plan file; ask clarifying questions; wait for user plan approval | Write product code, run fix commands, commit, start building before plan approval |
| **Reviewer** | Findings only (severity + path + why + direction) | Patches, drive-by refactors, executing fixes |
| **Builder** | Branch, TDD implement, run tests / lints / sandbox / browser, commit / merge | Soften acceptance criteria; skip approved scope without a plan revision |

## 4. Phases

```text
Plan → Plan-review → Build (TDD) → Review → (if findings) Build → Review … ≤3
  → Tests → Manual → Merge to dev
```

### Plan — Role: Planner

1. Load the item. Acceptance criteria = DoD.
2. Research files (readonly). Cite concrete paths.
3. CreatePlan: approach, files to change, TDD angle, which `make check-mXX` and which learner browser path gate merge.
4. Hand off to Plan-review. If findings → Planner revises the plan (no coding).
5. **Stop until the user approves the plan.** Then Builder starts.

### Plan-review — Role: Reviewer

Findings only vs acceptance, out of scope, and feasibility. Planner updates the plan.

### Build — Role: Builder

Execute the approved plan. TDD: failing tests first, then implement. UV + pytest. Only the Builder edits code.

**Delivery-only guards vs course tests:** Prefer real course tests (`tests/test_*.py` that learners / modules already own). If you add a temporary assert (e.g. `tests/test_v2_0xx_*`) only to drive a docs/YAML backlog fix, that file is **not** course content. Once it is green and acceptance is met, **delete it before merge** — do not ship implementation-check scaffolding in `tests/`.

### Review — Role: Reviewer

Run **all four lenses** on the diff (sequential or findings-only subagents). Never edit.

| Lens | Looks for |
|------|-----------|
| **Security** | Secrets, unsafe defaults, auth / CORS / host drift, injection, privilege, supply-chain |
| **Code** | SOLID, bugs, logical gaps / loops, smells, docs drift, scope creep vs the card |
| **Lints** | `uv run ruff check .` / `uv run ruff format --check .` / `uv run mypy src/` — failures are findings |
| **UI/UX** | Learner docs/UI: broken commands, empty or misleading UI, nip.io steps not executable |

Finding format: [reference.md](reference.md). Direction, not a patch.

### Build ↔ Review loop

1. Builder finishes a build pass.
2. Reviewer runs all four lenses.
3. Open findings → Builder fixes → review again.
4. **Max 3 cycles** (one cycle = build + review). After 3 with leftover findings: **stop**, report blockers, do not merge.
5. Zero findings → Tests → Manual → Merge.

### Tests — Role: Builder

Touch-dependent commands in [reference.md](reference.md). Typical: `make precommit`, `make docs-build` if docs/reference changed, `make check-mXX` for touched modules (`check-m01` / `check-m03` need live k3d).

Root `tests/` does not cover platform YAML. Green pytest is not enough.

Before merge: confirm no leftover `tests/test_v2_0xx_*` (or similar) delivery-only guards remain — remove them if still present and green.

### Manual — Role: Builder (merge blocker)

Mimic a real learner. Green CI alone fails this gate.

1. Sandbox up if needed: `uv sync` → `make configure-ip` → `cp -n .env.example .env` → `make cluster-up` → `make urls`. Module deploy: `reference/mNN/_deploy.sh` or `make catchup-mNN`.
2. Open the **module docs** this change touches (`make docs` or MkDocs URL). Follow the written steps as a new learner.
3. Browser tools: navigate, snapshot, click the UIs the docs name. Run the **exact** commands from the docs.
4. Pass = docs commands work, UIs match expected state, and card pre-flight curls succeed.
5. Fail = no merge. Builder fixes or re-enter review. Record what was clicked / run.

URLs: `http://{mlflow|minio|s3|dagster}.$SERVER_IP.nip.io:8080`. M4 local Dagster: `http://$SERVER_IP:3000` with `DAGSTER_HOME=$PWD/.dagster_home`. Card pre-flight (CORS curl, `sqlite3 … runs.db`, health) **plus** the browser path, not instead of it.

### Merge — Role: Builder

Only after Tests **and** Manual pass. Ask once before push / merge unless the user already asked. Target: `dev` only.

## 5. Out of scope

- Release / merge to `main`
- Inventing backlog items unless asked
- Softening acceptance criteria
