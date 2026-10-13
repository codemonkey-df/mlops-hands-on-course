# On-prem MLOps hands-on course

A 12-module course that builds a complete on-prem MLOps platform on a k3d
Kubernetes cluster (designed for a Proxmox LXC): Dagster, MLflow, DVC, MinIO,
Postgres, BentoML, mocked vLLM + LiteLLM router, Gitea CI, Harbor, ArgoCD,
KEDA, Prometheus and Grafana.

Synthetic data only. vLLM is mocked (real chart/args/metrics/router); no cloud
required.

## Start the course site

```bash
uv sync
make docs            # http://<host-ip>:8000  (live reload)
```

All module pages, diagrams, and exercise instructions live on the site.
Cheat sheets are under **Cheat sheets** in the nav.

## Layout

| Path | Role |
|------|------|
| `docs/` | Course pages (MkDocs Material) |
| `reference/mNN/` | Verified solution for module N — answer key, embedded in the docs |
| `src/`, `platform/`, `infra/` | **Your** working tree (what you build while learning) |
| `exercises/mNN/` | Planted bugs + `make check-mNN` verifiers |
| `Makefile` | `docs`, cluster lifecycle, `check-mNN`, `catchup-mNN` |

## Important: `src/` may already look “done”

This repo ships with a **complete reference implementation**. After cloning you
may see full code under `src/`, `platform/`, and `infra/`. That is the **answer
key state** (used to verify the course), not “you finished without reading.”

Learning happens by following each module page and **building or changing**
your tree, then running the break/fix exercises — not by assuming the
checked-in `src/` means there is nothing left to do.

| Path | Treat as |
|------|----------|
| `reference/mNN/` | Peek when stuck; don’t edit as your main work |
| `src/`, `platform/`, `infra/` | Your desk — recreate, tweak, or clear and rebuild |
| `exercises/mNN/` | Required practice (`make check-mNN`) |

Stuck or short on time: `make catchup-mNN` copies `reference/mNN/` into your
tree (with a backup) and runs that module’s deploy script.

## How to take the course

Every module page has the same loop: **problem → foundations → build →
tweak → break/fix → gotchas**.

Pick a path:

**A — Best for learning (recommended)**  
Clear or rename the parts of `src/` / `platform/` you want to redo. Open the
site, start at **M0**, recreate files from the page into your folders, then
`make check-mNN`. Peek `reference/` only when stuck.

**B — Faster (cluster / code already present)**  
Keep the solved tree. Still read foundations and gotchas on each page, and
**do every exercise**: `make check-m00`, `check-m01`, … That is where most of
the practice is.

**C — Hybrid**  
`make catchup-mNN` through modules you already know (e.g. Git/CI), then build
the next modules yourself (Dagster, ArgoCD, LLM, KEDA, …).

### Daily commands

```bash
make docs            # course site
make cluster-up      # first time: create k3d cluster
make cluster-start   # after reboot (state kept)
make cluster-stop    # free RAM for the day
make urls            # Ingress / UI hosts
make check-m03       # all exercises for a module
make check-m03 BUG=bug01
make catchup-m03     # copy reference + deploy
make help
```

Copy `.env.example` → `.env` before training / MLflow clients from the host.

## Requirements (high level)

- Privileged LXC (or similar) with Docker, enough RAM (~16+ GB free for the
  full stack), and `/dev/kmsg` usable by kubelet (see M0)
- `uv`, Python 3.12; CLIs installed by M0 (`kubectl`, `helm`, `k3d`, `k9s`, `dvc`)
- Optional GPU: real DCGM exporter bonus in M10; vLLM stays mocked by default

Details and the architecture diagram are on the site home page.
