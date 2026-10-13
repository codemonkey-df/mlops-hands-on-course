# Gotchas (all modules)

The short list worth remembering. Each module page has the longer version.

## Cluster (M0, M1)

- Check `kubectl config current-context` before every delete.
- `/dev/kmsg` in an LXC: the device node existing ≠ the cgroup allowing it. k3d binds `/dev/null` over it.
- `k3d cluster stop` keeps state; `delete` is a wipe.
- Prefix manifest files (`00-`, `10-`): `kubectl apply -f dir/` is alphabetical.
- RWO volume + Deployment → `strategy: Recreate` (or use a StatefulSet).
- Selector labels are immutable. Never put the version in them.
- Helm: quote strings that look like numbers. Always `helm template` before apply.
- A Kubernetes Secret in Git is a credential leak. Base64 is not encryption.

## Data (M2)

- One seeded `np.random.default_rng(seed)` per process. Never `np.random.*` globals.
- Commit `dvc.lock`. Ignore the data files.
- MinIO is path-style S3: explicit endpoint, any region (`us-east-1`).
- The DVC remote is a cache. Consumers read the lake (Hive Parquet).

## MLflow (M3)

- `postgresql+psycopg://` — SQLAlchemy 2.1 picks the wrong driver otherwise.
- `--serve-artifacts`: only the server holds S3 credentials.
- Aliases (`@champion`), not stages. Promote by moving the pointer.
- Compare challenger vs champion on the **same** fresh data.
- Always pass `step=` for per-epoch metrics. `model.eval()` + `torch.no_grad()` at inference.

## Dagster (M4, M5)

- Asset parameter names **are** dependencies. A typo creates a new upstream.
- Unpartitioned downstream of partitioned upstream loads **all** partitions. Use `deps=` + a query.
- `LastPartitionMapping` is the last partition of the *definition*, not the last materialized one.
- Sensors must advance a cursor. `run_key` is the second safety net.
- Never read secrets at import time (`dg.EnvVar`).
- The webserver never imports your code — debug the **code server** pod.
- `includeConfigInLaunchedRuns`, or run pods lack env.
- `IfNotPresent` when using `k3d image import` (chart default is `Always`).

## Serving (M6)

- Resolve `@champion` at **build** time. The image tag then says what is served.
- `BentoModel("...:latest")` is the most recently *imported* model, not the highest version.
- Signature dtypes: cast at the edge. `int64` vs `int32` is the classic 500.
- `preStop: sleep 5` — endpoint removal is asynchronous.
- Memory = workers × model size.

## CI + Harbor (M7)

- Push name (`127.0.0.1:8085`) ≠ pull name (`harbor.local:8085`) in this lab.
- Immutable SHA tags, never `latest`.
- Secrets through `env:` + `--password-stdin`. Never `${{ secrets.X }}` inside `run:`.
- No `uses:` from github.com on an air-gapped runner.

## GitOps (M8)

- Git is the only write path. `kubectl edit` is reverted (`selfHeal`) or forgotten.
- CI commits tags; it never runs `kubectl`.
- `[skip ci]` **and** `paths-ignore` on the GitOps folder, or CI loops.
- Waves: CRDs at `-1`, workloads at `0+`.
- `resources-finalizer` → deleting the Application deletes its resources.

## LLM (M9)

- `--served-model-name` = router `hosted_vllm/<name>`.
- `api_base` ends in `/v1`.
- `startupProbe` for every model server. Liveness `timeoutSeconds` > 1.
- One GPU, one pod: `Recreate` (or `maxSurge: 0`).
- `/dev/shm` in-memory emptyDir, or tensor-parallel vLLM dies with `Bus error`.
- `HF_HUB_OFFLINE=1`, `LITELLM_LOCAL_MODEL_COST_MAP=True`.
- Retry in **one** place (the router). Client `max_retries=0`.

## Observability + KEDA (M10)

- ServiceMonitor `release` label = Helm release name (`kube-prometheus-stack`).
- `prometheus.io/scrape` annotations are a no-op with the operator.
- vLLM metric names contain a **colon**. Underscores return empty vectors.
- Queue scalers: `metricType: Value`. AverageValue hides load behind replica count.
- `cooldownPeriod` is 1→0 only. 4→1 is HPA `stabilizationWindowSeconds`.
- HTTP + `minReplicas: 0` never recovers without an interceptor.

## Capstone (M11)

- MLflow `@champion` ≠ the running image. Check `/model_info`.
- Rollback is `git revert`, not `kubectl rollout undo`.
- Work backwards along the sequence diagram. Skipping hops wastes the evening.
