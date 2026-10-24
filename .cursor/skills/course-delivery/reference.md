# Course delivery — checklists

Copy the phase block into chat at start. Tick as you go. Announce `Role:` on each switch.

## Phase checklist

```text
Item: V2-0xx
Branch: (from dev) fix/V2-0xx-…
Cycle: 0/3

[ ] Role: Planner — plan created, files cited, gates named
[ ] Role: Reviewer — plan-review (findings only)
[ ] Role: Planner — plan revised if needed; user approved
[ ] Role: Builder — TDD build pass
[ ] Role: Reviewer — four lenses (cycle 1/3)
[ ] Role: Builder — fix findings (if any)
[ ] Role: Reviewer — four lenses (cycle 2/3)   # skip if zero findings
[ ] Role: Builder — fix findings (if any)
[ ] Role: Reviewer — four lenses (cycle 3/3)   # skip if zero findings
[ ] Role: Builder — Tests gate
[ ] Role: Builder — remove green delivery-only guards (`tests/test_v2_0xx_*`) if any
[ ] Role: Builder — Manual learner walkthrough
[ ] Role: Builder — merge to dev (ask first)
```

After 3 cycles with leftover **blocker** / **should-fix**: stop. Report blockers. Do not merge.

## Finding template

One block per finding. Direction, not a patch.

```text
- severity: blocker | should-fix | nit
  lens: security | code | lints | ui-ux
  path: path/to/file:line
  problem: …
  direction: …
```

- **blocker** — must fix this cycle or stop merge
- **should-fix** — must fix before merge unless user waives
- **nit** — optional; do not burn a cycle alone

## Tests gate

Run what the change touched.

```bash
make precommit
# ruff + mypy + pytest (tests/ only; no cluster)

make docs-build
# if docs/ or reference/ snippets changed

make check-m01   # live k3d
make check-m03   # live k3d
make check-m04   # in-process
# only modules the card / diff touches

# optional maintainer
make verify-mNN
```

**Delivery-only guards:** Temporary `tests/test_v2_0xx_*` (or similar) files that only assert the backlog fix landed are **not** course tests. After they pass and the card is otherwise Done, **delete them before merge** — do not leave implementation scaffolding in `tests/`.

## Manual gate

Record commands and browser steps actually run.

```text
Sandbox:
[ ] uv sync / configure-ip / .env / cluster-up / urls (if needed)
[ ] catchup-mNN or reference/mNN/_deploy.sh (if needed)

Docs followed (paths):
- …

Browser (learner path):
- URL:
- clicks / tabs:
- expected vs actual:

Doc commands (exact):
- …

Card pre-flight (if any):
- …
```

### URL patterns

- Ingress: `http://{mlflow|minio|s3|dagster}.$SERVER_IP.nip.io:8080`
- M4 local: `http://$SERVER_IP:3000` with `DAGSTER_HOME=$PWD/.dagster_home`

### Discover hosts

```bash
make urls
```
