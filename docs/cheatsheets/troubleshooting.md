# Troubleshooting

Work top-down: cluster → namespace → pod events → logs → the next hop's identity (`/model_info`, Prometheus targets, Argo CD sync).

## k3d / kubelet never becomes Ready

| You see | Likely cause | Fix |
|---|---|---|
| `open /dev/kmsg: operation not permitted` | LXC cgroup blocks the device | `lxc.cgroup2.devices.allow: c 1:11 rwm` on the Proxmox host, or the `/dev/null:/dev/kmsg` volume in the k3d template |
| `k3d cluster create` hangs | Agents missing the kmsg bind | `nodeFilters: [server:*, agent:*]` |
| `NotReady` after LXC reboot | Node containers are stopped | `make cluster-start` |

## Image pull

| You see | Likely cause | Fix |
|---|---|---|
| `http: server gave HTTP response to HTTPS client` | containerd talking HTTPS to Harbor | k3d `registries.config` mirror for `harbor.local:8085` |
| `unauthorized` | Missing pull secret in that namespace | `infra/compose/harbor/k8s-pull-secret.sh <ns>` |
| `ImagePullBackOff` with `Always` | Tag not in Harbor / k3d import + Always | Pin the tag; `imagePullPolicy: IfNotPresent` for imported images |

## Pod crash loops

| You see | Likely cause | Fix |
|---|---|---|
| `OOMKilled` | Limit too low (Bento workers × model) | Raise memory; fewer workers |
| `Startup probe failed` forever | Probe budget < load time | `periodSeconds × failureThreshold` ≥ worst-case load |
| `Bus error` in vLLM | `/dev/shm` is 64 MiB | in-memory emptyDir 2Gi |
| MLflow / Dagster `NoSuchModuleError: psycopg` | SQLAlchemy 2.1 default driver | `postgresql+psycopg://` or `+psycopg2` |

## Empty Grafana / KEDA stuck at min

| You see | Likely cause | Fix |
|---|---|---|
| `/metrics` works, target missing | ServiceMonitor `release` label | Must be `kube-prometheus-stack` |
| Target UP, graph empty | Wrong PromQL name | Colon in `vllm:*`; copy from `/metrics` |
| Waiting=20, HPA metric=0 | `vllm_num_requests_waiting` (underscore) | `vllm:num_requests_waiting` |
| Load high, no extra replicas | `metricType` default AverageValue | Set `metricType: Value` |
| Scaled to 0, never returns | HTTP + minReplicas 0 | minReplicas 1, or http-add-on |
| Replica sawtooth | No scaleDown window | `stabilizationWindowSeconds: 120` |

## LLM 404s

| Body | Cause |
|---|---|
| `The model \`models/small-chat\` does not exist` | Missing `--served-model-name`; vLLM defaulted to the weights path |
| FastAPI `{"detail":"Not Found"}` | `api_base` missing `/v1` |

## GitOps "it didn't deploy"

1. Did CI commit the tag into **`platform/gitops/`** (not `platform/k8s/`)?
2. Is the Application `Synced`? If `OutOfSync` forever → `automated` missing.
3. Is it `Synced` + `Degraded`? Image/probe problem, not GitOps.
4. `/model_info` still old after a green CI → you promoted MLflow but baked the previous champion, or the tag file is wrong.

## Dagster sensor silent

- Cursor not advanced → it re-scans the same events (or none).
- `PSI_ALERT` set above any real PSI (e.g. 2.0).
- Sensor not started: code location didn't load (`validate_loadable` in tests).

## IP / Ingress drift {#ip-ingress-drift}

| You see | Likely cause | Fix |
|---|---|---|
| `curl: (6) Could not resolve host` / empty `$SERVER_IP` | IP never set, or shell missing `export` / `.env` | `hostname -I \| awk '{print $1}'`, then `make configure-ip`; `source .env` |
| Browser opens `….201.nip.io` but cluster was built for `.202` | Ingress / CORS / `.env` disagree | Re-run the [One IP everywhere](../modules/m00-environment.md#step-4-set-your-server-ip) checklist; re-apply Ingress + MLflow Deployment |
| nip.io fails from another network, but Traefik is up | DNS path only | `curl -H "Host: minio.$SERVER_IP.nip.io" http://127.0.0.1:8080` — if that works, the app is fine |

## Python package / editable install

| You see | Likely cause | Fix |
|---|---|---|
| `No module named 'mlops_course'` with `uv run python` | Broken or empty editable install (`pytest` still works via `pythonpath = ["src"]`) | `uv sync --reinstall-package mlops-course`, or `PYTHONPATH=src uv run python …` |
| Bare `uv run pytest` ImportError for `training` / `pipelines` / `serving` mid Path A | Repo `tests/` covers later modules; your tree only has what you've built | Run the **current** module file, e.g. `uv run pytest -q tests/test_data_generator.py`; `make catchup-mNN` or finish modules before `make precommit` |

## MLflow / MinIO / Dagster empty UI (M1–M4)

| You see | Likely cause | Fix |
|---|---|---|
| Runs tab `INTERNAL_ERROR` (CORS) | Missing `--cors-allowed-origins=http://mlflow.<IP>.nip.io:8080` | Add the flag next to `--allowed-hosts`, `kubectl apply -f platform/k8s/mlflow/`, rollout; smoke with the Origin curl in M3 |
| `exec: "kill": executable file not found` on MinIO | Distroless/Chainguard image has no `kill` | `kubectl -n storage rollout restart deploy/minio` (or `delete pod -l app.kubernetes.io/name=minio`); watch EndpointSlices |
| Overview “Failed to load chart data” after a good train | MLflow 3 GenAI **Overview**; classic experiments live under **Runs** | Open **Experiments → churn → Runs**, not Overview |
| Train OK, MLflow UI empty / local `./mlruns/` | `MLFLOW_TRACKING_URI` not in process env (`.env` feeds S3 via pydantic, not MLflow) | `set -a && source .env && set +a` in **every** shell before `uv run … train` |
| Materialize prints success; UI `/runs` empty | CLI used a different/`unset` `DAGSTER_HOME` than `dagster dev` | Same `export DAGSTER_HOME=$PWD/.dagster_home` in every terminal; `sqlite3 "$DAGSTER_HOME/history/runs.db" "SELECT count(*) FROM runs;"` |
| Pod ~96% MEM in `kubectl top` / k9s | That % is usually of the **request**, not the limit | Near the **limit** → OOM risk; compare `kubectl describe pod` requests vs limits |

## Disk / RAM

```bash
docker system df
docker image prune
k3d cluster stop          # free RAM overnight, keep PVCs
kubectl top nodes
```
