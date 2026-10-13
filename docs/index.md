# On-prem MLOps, hands-on

You'll build this platform from an empty Docker host, one component per module:

```mermaid
flowchart LR
    gen[SyntheticDataGen] --> minio
    dev[You] --> gitea[Gitea]
    gitea --> runner[act_runner CI]
    runner --> harbor[Harbor]
    gitea --> argocd
    harbor --> argocd
    subgraph k3d [k3d Kubernetes cluster]
        dagster[Dagster] --> jobs[TrainingJobs]
        jobs --> mlflow[MLflow]
        jobs --> minio[MinIO]
        mlflow --> postgres[Postgres]
        argocd[ArgoCD] --> bento[BentoML]
        argocd --> vllm["vLLM mock, one Deployment per model"]
        router[LiteLLM router] --> vllm
        minio -->|"fake weights via initContainer"| vllm
        keda[KEDA] --> vllm
        prom[Prometheus] --> grafana[Grafana]
        bento --> prom
        vllm --> prom
        dcgm["DCGM mock exporter"] --> prom
    end
    apps[ClientApps] --> router
    apps --> bento
```

## Where this course was built

This material was developed and verified inside a **privileged LXC container on
Proxmox** (Ubuntu + Docker + k3d). That is a convenient on-prem lab, not a hard
requirement.

You can run the same stack on a **plain Linux VM** (Proxmox QEMU/KVM, VirtualBox,
VMware, cloud VM) or any machine with Docker — as long as you have enough RAM
(~16+ GB free for the full platform), can create a k3d cluster, and set
`YOUR_SERVER_IP` to that host’s LAN IP (`make configure-ip`). Nested Kubernetes
gotchas that show up in LXC (for example `/dev/kmsg`) are called out in **M0**;
on a normal VM they usually do not appear.

## How each module works

Every module page has the same six sections. Go through them in order:

| Section | What you do |
|---|---|
| **1. Problem to solve** | Read which gap in the pipeline the new tool closes. |
| **2. Foundations** | Learn the mental model and vocabulary. It's short; search the YouTube keywords for demos. |
| **3. Build it step by step** | Type or copy the code into your own folders, run it, and compare with *"You should see"*. |
| **4. Tweak and observe** | Change one thing, predict what happens, run it, compare. |
| **5. Break and fix** | Planted bugs in `exercises/mNN/`. Run `make check-mNN` until everything is green. |
| **6. Gotchas** | The short list worth remembering. |

!!! tip "Where things live"
    - `reference/mNN/` holds the verified solution for every file you build. The pages embed these files, so what you read is code that has actually run.
    - **Your** work goes into `src/`, `platform/` and `infra/`.
    - Stuck or short on time? `make catchup-mNN` copies the reference into your tree (backing up your files) and deploys it.

!!! info "Solutions are hidden"
    Hints and solutions are in collapsed boxes like this one. Try for a few minutes before opening them.

    ??? success "Solution (example)"
        Hidden until you click.

## Progress

- [ ] M0 Environment: tools, k3d cluster, this site
- [ ] M1 Kubernetes + Helm: MinIO (raw manifests), Postgres (your own Helm chart)
- [ ] M2 Synthetic data, DVC, DuckDB
- [ ] M3 MLflow tracking + registry
- [ ] M4 Dagster foundations (local)
- [ ] M5 Dagster on Kubernetes
- [ ] M6 BentoML serving
- [ ] M7 Gitea CI + Harbor
- [ ] M8 ArgoCD GitOps
- [ ] M9 LLM serving: vLLM mock + LiteLLM router
- [ ] M10 Prometheus, Grafana, KEDA
- [ ] M11 Capstone: drift to deploy, incident drill

## Daily commands

```bash
make configure-ip    # replace YOUR_SERVER_IP with this host's LAN IP
make docs            # this site
make cluster-start   # after a reboot (state is kept)
make cluster-stop    # free RAM when you're done for the day
make urls            # list all web UIs
make help            # everything else
```
