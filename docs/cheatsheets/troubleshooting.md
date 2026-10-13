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

## Disk / RAM

```bash
docker system df
docker image prune
k3d cluster stop          # free RAM overnight, keep PVCs
kubectl top nodes
```
