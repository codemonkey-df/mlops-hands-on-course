---
id: V2-008
title: Elective track — AI systems engineer path
status: ready
track: elective
priority: high
effort: L
modules: [E-systems, E-slurm, E-eval, E-train, E-data, E-rag]
area: elective
depends_on: [V2-009]
---

# V2-008: Elective track — AI systems engineer path

## Problem

The core M0–M11 path teaches the platform loop (Dagster → train/serve →
MLflow → GitOps). It does **not** prepare a learner to join a team that
builds and operates large LLM systems: Slurm queues, distributed
training, time-boxed evaluation, corpus hygiene, and interview-ready
system judgment.

## Why it matters for v2

Offer a **high-priority elective curriculum** for the next course version:
enough depth to understand what experts discuss (Slurm, training, eval,
data) and to reason about systems — not deep specialization in every
area. Same module loop as the course: problem → basics → build → tweak →
break/fix → gotchas.

Recommended for the **AI Systems Engineer** persona in **V2-009**.

## Proposed change

- Add an **opt-in track** (docs under e.g. `docs/electives/ai-systems/` or
  epic folders). Default M0–M11 unchanged.
- Ship as ordered epics (tasks below). Prefer splitting implementation
  into follow-up cards when a single epic becomes a PR of its own.
- **V2-006** is `wontfix` (superseded by Epic 1 here). Keep Spark
  (**V2-007**) as a separate elective — not the same as Epic 4.
- Home / progress: list this track as *optional; target: AI systems
  engineer readiness*. Wire into path chooser (**V2-009**).

### Work order

**Epic 1 → Epic 3 → Epic 2 → Epic 4 → Epic 5 → Epic 6.**  
Epic 5 may be deferred if time runs out.

### Task statuses (within this track)

`To Do` / `In Progress` / `Done` (mirror course workflow).

---

## Epic 1: Slurm (priority high)

### task-1: Local Slurm cluster in Docker

- status: To Do | labels: slurm, hpc, epic-1 | priority: high | depends on: —
- **Description:** Stand up a small Slurm cluster (controller + 2 compute
  nodes + accounting) to understand job queueing.
- **Acceptance Criteria:**
  - [ ] `sinfo` shows 2 nodes idle
  - [ ] `sbatch` runs a simple job; `sacct` shows its history
  - [ ] Break/fix: broken `slurm.conf`, diagnose from `slurmctld` logs
  - [ ] Gotchas note in `docs/`

### task-2: Slurm basics: sbatch, srun, squeue, scancel, sacct

- status: To Do | labels: slurm, epic-1 | priority: high | depends on: task-1
- **Description:** Master the basic job lifecycle and resource requests.
- **Acceptance Criteria:**
  - [ ] `sbatch` script with `--cpus-per-task`, `--mem`, `--time`, `--output`
  - [ ] Job exceeds `--time` and is killed; show that in `sacct`
  - [ ] Difference `srun` vs `sbatch` explained in own words

### task-3: Partitions, QOS, and priorities

- status: To Do | labels: slurm, epic-1 | priority: medium | depends on: task-1
- **Description:** Understand how Slurm decides which job starts first.
- **Acceptance Criteria:**
  - [ ] Two partitions (e.g. `short`, `long`) with different limits
  - [ ] Observed start-order difference under different priorities/QOS
  - [ ] Note on fairshare and backfill

### task-4: GRES and GPUs in Slurm

- status: To Do | labels: slurm, gpu, epic-1 | priority: high | depends on: task-1
- **Description:** Configure GPU resources (real or fake in `gres.conf`)
  and request them from jobs.
- **Acceptance Criteria:**
  - [ ] `--gres=gpu:1` correctly allocates the resource
  - [ ] Two jobs do not get the same GPU (`CUDA_VISIBLE_DEVICES`)
  - [ ] Break/fix: job asks for more GPUs than exist and stays pending
        with a readable reason

### task-5: Job arrays and inter-job dependencies

- status: To Do | labels: slurm, epic-1 | priority: high | depends on: task-2
- **Description:** Run many similar tasks in parallel and chain them.
- **Acceptance Criteria:**
  - [ ] `--array=0-9%3` with concurrency cap
  - [ ] Aggregator job with `--dependency=afterok:<array_id>`
  - [ ] Behaviour when one array element fails documented and verified

### task-6: Containers in Slurm jobs (Apptainer or Enroot)

- status: To Do | labels: slurm, containers, epic-1 | priority: medium | depends on: task-2
- **Description:** Run a Python/PyTorch environment in a container inside
  a job.
- **Acceptance Criteria:**
  - [ ] Job runs a container image and executes a script
  - [ ] Data bind-mounted; GPU accessible inside the container
  - [ ] Note: why HPC uses Apptainer/Enroot instead of Docker

### task-7: Dagster → Slurm

- status: To Do | labels: slurm, dagster, epic-1 | priority: high | depends on: task-5
- **Description:** Dagster asset that submits an `sbatch` job, waits for
  completion, and collects the result.
- **Acceptance Criteria:**
  - [ ] Asset submits the job and polls status (`squeue`/`sacct`)
  - [ ] Job logs visible in the Dagster UI
  - [ ] Job failure and timeout handling

---

## Epic 2: PyTorch + Hugging Face

### task-8: Training loop from scratch

- status: To Do | labels: pytorch, training, epic-2 | priority: high | depends on: —
- **Description:** Write a custom training loop for a small model, without
  Trainer.
- **Acceptance Criteria:**
  - [ ] bf16/mixed precision, gradient accumulation, scheduler
  - [ ] Model and optimizer checkpoints
  - [ ] Resume from checkpoint yields a coherent loss curve

### task-9: Hugging Face datasets + Trainer + non-English tokenization

- status: To Do | labels: huggingface, nlp, epic-2 | priority: medium | depends on: task-8
- **Description:** Move from a custom loop to the HF ecosystem.
- **Acceptance Criteria:**
  - [ ] Dataset processed and saved (`datasets` + Parquet)
  - [ ] Training via `Trainer` on a non-English (e.g. Polish) corpus
  - [ ] Note: tokenization differences (sequence length, cost)

### task-10: Fine-tuning LoRA/QLoRA (PEFT)

- status: To Do | labels: peft, finetuning, epic-2 | priority: high | depends on: task-9
- **Description:** Fine-tune a small model with LoRA/QLoRA.
- **Acceptance Criteria:**
  - [ ] PEFT training logged to MLflow
  - [ ] Adapter merged and result served with vLLM
  - [ ] Note: memory use vs full fine-tuning

### task-11: Multi-GPU with Accelerate / DDP

- status: To Do | labels: distributed, epic-2 | priority: medium | depends on: task-8
- **Description:** Understand data parallelism (on GPU or CPU with `gloo`).
- **Acceptance Criteria:**
  - [ ] Training on 2 processes via `torchrun`/`accelerate launch`
  - [ ] Explained: rank, world size, all-reduce, distributed sampler
  - [ ] Break/fix: hung training from mismatched rank/port settings

### task-12: FSDP and DeepSpeed ZeRO

- status: To Do | labels: distributed, deepspeed, epic-2 | priority: low | depends on: task-11
- **Description:** Learn how memory is sharded for large models.
- **Acceptance Criteria:**
  - [ ] One FSDP or ZeRO (stage 2/3) config run successfully
  - [ ] Comparison note: DDP vs FSDP vs ZeRO (memory, communication,
        when to use which)

### task-13: Training on Slurm (sbatch + torchrun) with resume

- status: To Do | labels: slurm, training, epic-2 | priority: high | depends on: task-5, task-11
- **Description:** Combine distributed training with the job queue.
- **Acceptance Criteria:**
  - [ ] `sbatch` script with `torchrun` and Slurm-provided env vars
  - [ ] Mid-job kill resumes from checkpoint (e.g. via requeue)
  - [ ] Note on preemption and checkpointing

---

## Epic 3: Evaluation under a time budget

### task-14: lm-evaluation-harness with a local model (vLLM)

- status: To Do | labels: eval, vllm, epic-3 | priority: high | depends on: —
- **Description:** Run a standard eval harness with a vLLM backend.
- **Acceptance Criteria:**
  - [ ] Small model evaluated on a chosen benchmark
  - [ ] Results saved in a structured format (JSON)
  - [ ] Time and resource use documented

### task-15: Custom eval task (non-English)

- status: To Do | labels: eval, nlp, epic-3 | priority: medium | depends on: task-14
- **Description:** Define a custom harness task (YAML) on non-English data.
- **Acceptance Criteria:**
  - [ ] Task in repo, runnable with one command
  - [ ] Metric and prompting approach documented

### task-16: Time budget: throughput and vLLM tuning

- status: To Do | labels: eval, performance, epic-3 | priority: high | depends on: task-14
- **Description:** Measure and improve eval throughput.
- **Acceptance Criteria:**
  - [ ] Tokens/s measured across `max_num_seqs`, batches, prefix caching
  - [ ] Results table and bottleneck identified
  - [ ] Conclusion: how long a full eval takes on the given hardware

### task-17: Parallel eval via job array

- status: To Do | labels: eval, slurm, epic-3 | priority: high | depends on: task-5, task-14
- **Description:** Shard the dataset, run in parallel, aggregate.
- **Acceptance Criteria:**
  - [ ] N shards as job-array elements
  - [ ] Aggregator job merges results (`afterok` dependency)
  - [ ] Result matches sequential evaluation

### task-18: Result cache, subsets, timeouts, retry

- status: To Do | labels: eval, reliability, epic-3 | priority: medium | depends on: task-17
- **Description:** Harden and speed up evaluation.
- **Acceptance Criteria:**
  - [ ] Model-response cache (rerun does not recompute from scratch)
  - [ ] Sampled subset (fixed seed) for fast runs
  - [ ] Timeouts and retries for failed examples

### task-19: Dagster asset: eval → MLflow with regression detection

- status: To Do | labels: eval, dagster, mlflow, epic-3 | priority: high | depends on: task-7, task-17
- **Description:** Automate evaluation as part of the pipeline.
- **Acceptance Criteria:**
  - [ ] Asset runs eval and logs metrics to MLflow
  - [ ] Baseline comparison and asset check on quality drop
  - [ ] Break/fix: deliberately worse model is detected

### task-20: Note — “fit eval into 1 hour”

- status: To Do | labels: eval, docs, epic-3 | priority: medium | depends on: task-16, task-18
- **Description:** Capture takeaways in a form you can explain in an
  interview.
- **Acceptance Criteria:**
  - [ ] One page: time budget, levers (batching, shards, subsets, cache),
        quality/time trade-offs

---

## Epic 4: Large-scale text data

### task-21: Corpus ingest → Parquet in MinIO (Polars)

- status: To Do | labels: data, polars, minio, epic-4 | priority: medium | depends on: —
- **Description:** Read raw texts and write them in a structured format.
- **Acceptance Criteria:**
  - [ ] Pipeline reads source files and writes Parquet to MinIO
  - [ ] Schema (id, text, source, metadata) documented

### task-22: Quality filters

- status: To Do | labels: data, quality, epic-4 | priority: medium | depends on: task-21
- **Description:** Drop low-quality documents.
- **Acceptance Criteria:**
  - [ ] Filters: language, length, character ratio, repetition
  - [ ] Report: how many documents dropped and why

### task-23: Deduplication (exact + MinHash)

- status: To Do | labels: data, dedup, epic-4 | priority: high | depends on: task-21
- **Description:** Remove duplicates and near-duplicates.
- **Acceptance Criteria:**
  - [ ] Exact dedup (hash) and approximate (MinHash/LSH)
  - [ ] Measurement: removal rate and effect of similarity threshold

### task-24: PII anonymization

- status: To Do | labels: data, privacy, epic-4 | priority: medium | depends on: task-21
- **Description:** Detect and mask personal data.
- **Acceptance Criteria:**
  - [ ] Regex + checksum validation (e.g. national ID / tax ID) + NER for
        names
  - [ ] Test set with expected hits and precision/recall scores

### task-25: datatrove on Slurm

- status: To Do | labels: data, slurm, datatrove, epic-4 | priority: medium | depends on: task-5, task-23
- **Description:** Process a corpus in parallel via the Slurm executor.
- **Acceptance Criteria:**
  - [ ] datatrove pipeline run across several Slurm tasks
  - [ ] Runtime compared to a local run

### task-26: Corpus quality stats + DVC versioning

- status: To Do | labels: data, dvc, dagster, epic-4 | priority: medium | depends on: task-22, task-23
- **Description:** Wire stages into a pipeline with lineage and a report.
- **Acceptance Criteria:**
  - [ ] Dagster asset for the full flow (ingest → filters → dedup → PII)
  - [ ] Corpus version in DVC and a stats report

---

## Epic 5: RAG and agent (small project) — deferrable

### task-27: RAG: chunking, embeddings, pgvector

- status: To Do | labels: rag, pgvector, epic-5 | priority: low | depends on: —
- **Description:** Build a basic retrieve-and-answer pipeline.
- **Acceptance Criteria:**
  - [ ] Chunking, embeddings, index in pgvector
  - [ ] Query returns top-k chunks and a model answer with sources

### task-28: RAG evaluation

- status: To Do | labels: rag, eval, epic-5 | priority: low | depends on: task-27
- **Description:** Measure retrieval and answer quality.
- **Acceptance Criteria:**
  - [ ] Question set with expected sources
  - [ ] recall@k and RAGAS metrics (faithfulness, relevancy)

### task-29: Simple tool-use agent (MCP) via vLLM + FastAPI

- status: To Do | labels: agents, mcp, epic-5 | priority: low | depends on: task-27
- **Description:** Agent that calls tools, served by a local model.
- **Acceptance Criteria:**
  - [ ] Agent calls at least 2 tools (e.g. search + calculator)
  - [ ] FastAPI endpoint and call-trace logging

---

## Epic 6: Capstone and interview story

### task-30: End-to-end flow: Dagster → Slurm → GPU eval → MLflow

- status: To Do | labels: e2e, epic-6 | priority: high | depends on: task-7, task-19
- **Description:** One coherent pipeline that shows the full skill set.
- **Acceptance Criteria:**
  - [ ] Single run: data → (optional training) → eval → result in MLflow
  - [ ] Architecture diagram and README in repo
  - [ ] 5-minute demo recording or walkthrough notes

### task-31: Interview notes

- status: To Do | labels: interview, docs, epic-6 | priority: high | depends on: task-30
- **Description:** Prepare a story about architecture and decisions.
- **Acceptance Criteria:**
  - [ ] Answers for: why Slurm vs Kubernetes, how to scale eval, how to
        avoid corpus duplicates, how to resume training
  - [ ] List of trade-offs and “what I would improve”
  - [ ] Short honest gaps list (e.g. no large-scale FSDP experience)

---

## Acceptance criteria (track-level)

- [ ] Track is documented as elective; M0–M11 unchanged without it
- [ ] Epic order and task loop (problem → … → gotchas) are explicit in docs
- [ ] At least Epic 1 + Epic 3 ship as runnable labs in v2 (Epic 5 optional)
- [ ] Capstone-style path (task-30) ties Dagster → Slurm → eval → MLflow
- [ ] New checks (if any) are opt-in (`make check-e-systems` or per-epic), not
      forced into `check-m05` / `check-m11`
- [ ] Path chooser (**V2-009**) can recommend this track for the AI Systems
      Engineer role

## Out of scope

- Replacing the default K8s Job training path for all students
- Full production multi-cluster / multi-site federation at LLM scale
- Deep FSDP-at-scale ops experience (honest gap in task-31 is fine)
- Path-selection UX itself → **V2-009**

## Notes

**Track = elective, priority = high** for next course version — career /
team-readiness path, not a rewrite of v1.

**Dedup:**
- **V2-006** → `wontfix`; Slurm work lives only here (Epic 1 / 2 / 3 / 6).
- **V2-002** = core CI tiny holdout gate; Epic 3 / task-19 = elective
  harness + Slurm + Dagster regression asset — do not merge.
- **V2-007** (Spark) ≠ Epic 4 (Polars / datatrove / DVC); both may ship.

When an epic is too large for one PR, split into child cards
(`V2-008a`, …) and keep this file as the index of truth for task status.

## Done notes

_
