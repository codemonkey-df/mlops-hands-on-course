---
id: V2-009
title: Role-based learning paths (starter questions + personas)
status: ready
track: core
priority: high
effort: M
modules: [M0, home]
area: docs
depends_on: []
---

# V2-009: Role-based learning paths (starter questions + personas)

## Problem

Today every learner follows the same M0–M11 spine. Electives (**V2-007**,
**V2-008**) exist as cards, but nothing helps a student pick a coherent
route that still ends in a **working system** for *their* goal. People
aiming at platform MLOps vs AI systems / LLM ops need different depth at
different hops — without forking the course into unrelated silos.

## Why it matters for v2

Make the course **adaptive at the edges**: one shared platform core, then
guided choices (role or short starter quiz) that recommend which modules
to deepen, which electives to take, and which to defer — so the outcome
is still a functional pipeline suited to the chosen job shape.

## Proposed change

### 1. Job personas (named paths)

Define a small set of personas on the home / start page. Each maps to
**core spine + recommended electives + optional skips/depth**.

| Persona | Goal | Core | Lean into | Electives | Can defer |
|---------|------|------|-----------|-----------|-----------|
| **MLOps Engineer** | Ship and operate the v1 platform loop | Full M0–M11 | M5–M8, M11, CI/GitOps | — (or light V2-007 later) | Deep LLM training, Slurm |
| **AI Systems Engineer** | Train/eval/serve LLMs on batch + platform | M0–M4 + M7–M11 (serve/CI) | Eval, GPU serve (M9–M10) | **V2-008** (Epic 1→3→2→4→6; Epic 5 optional) | Spark (**V2-007**), full FSDP |
| **ML / Training Engineer** | Strong training + experiment loop | M0–M4, M7 | Training assets, MLflow, quality gates | V2-008 Epic 2 (+ task-13 if HPC) | Argo/KEDA depth, Spark |
| **Data / Platform Engineer** | Lakes, ETL, lineage at scale | M0–M2, M4–M5 | DuckDB/Polars, DVC, Dagster | **V2-007** and/or V2-008 Epic 4 | LoRA/FSDP, RAG agent |
| **LLM App / Applied AI** | RAG, agents, serving UX | M0–M1, M6, M9–M10 | Serving, LiteLLM, observability | V2-008 Epic 5 (RAG/agent) | Slurm clusters, Spark |

Names are working titles — keep tone professional (avoid slang like
“poor MLOps”); describe the **job shape**, not skill insult.

### 2. Starter questions (alternative to picking a persona)

Short quiz (5–7 questions) on first visit / M0. Examples:

- Do you care more about **shipping models to production** or **training /
  evaluating large models**?
- Is your target stack closer to **Kubernetes + GitOps** or **HPC / Slurm
  batch**?
- Will you own **data lakes / ETL**, **training loops**, or **serving /
  RAG apps**?
- How much time do you have (full spine vs spine + one elective)?
- GPU available? (yes / no / lab-only fake GRES)

Answers → recommended persona + module checklist (printable / progress
page). Learner can override anytime.

### 3. Progress / docs wiring

- Home page: “Choose your path” — personas **or** starter quiz.
- Progress tracker: show **required / recommended / optional** per
  chosen path; core M0–M11 still completable without electives.
- Each elective card links back: “Recommended for: AI Systems Engineer.”
- Capstone (M11) stays the default functional system; electives **extend**
  it (e.g. Slurm train hop) rather than replacing the happy path unless
  the persona explicitly swaps one hop (document the swap).

### 4. Constraint: one functional system

Whatever the learner chooses, docs must state the **minimum end state**:

- Data in lake → train or import model → registry → serve → (optional)
  observe — **or** the AI Systems variant: Dagster → Slurm → eval →
  MLflow, still with artifacts and a demo.

No dead-end elective stacks that never connect to serving or lineage.

## Acceptance criteria

- [ ] Home / M0 documents personas table and starter questions
- [ ] Each persona lists concrete module IDs + elective IDs (V2-007 / V2-008 epics)
- [ ] Progress UI (or markdown checklist) marks required vs optional for the
      active path
- [ ] Completing “MLOps Engineer” path = full M0–M11 without electives
- [ ] Completing “AI Systems Engineer” path = core subset + V2-008 (Epic 5
      optional) with a documented end-to-end demo
- [ ] Learner can change path mid-course without breaking already-done modules
- [ ] Docs / cheatsheet updated; `make check-m00` (or home check) still passes

## Out of scope

- Building a heavy adaptive LMS / paid assessment engine
- Autogenerating custom Docker stacks per persona
- Translating the whole course into multiple languages
- Implementing elective labs themselves → **V2-007**, **V2-008**

## Notes

**Track = core** (framing / UX for the course), even though it *surfaces*
electives. Priority high so electives are not orphaned lists.

Implement **V2-009 before or with** first elective ship so students know
*why* they open V2-008.

Soft dependency: V2-008 / V2-007 content can land in parallel, but path
docs should not recommend unfinished epics as required.

## Done notes

_
