# CLI reference

`YOUR_SERVER_IP` in files = this machine’s LAN IP. Discover it with
`hostname -I | awk '{print $1}'`, then `make configure-ip`. Most UIs are
`http://<name>.$SERVER_IP.nip.io:8080`.

## Course

| Command | What it does |
|---|---|
| `make configure-ip` | Replace `YOUR_SERVER_IP` with your LAN IP |
| `make docs` | MkDocs Material on `:8000` |
| `make cluster-up` / `cluster-stop` / `cluster-start` / `cluster-down` | k3d lifecycle |
| `make urls` | Print Ingress hosts |
| `make check-mNN` / `make check-mNN BUG=bug01` | Break/fix verifiers |
| `make catchup-mNN` | Copy reference + deploy (+ rewrites IP) |
| `make precommit` | ruff + mypy + pytest |

## Kubernetes

```bash
kubectl config current-context
kubectl get nodes,pods -A
kubectl -n llm get pods,hpa,scaledobject,servicemonitor
kubectl -n llm logs deploy/small-chat -c vllm --tail=50
kubectl -n llm logs deploy/small-chat -c dcgm --tail=20
kubectl -n llm port-forward svc/small-chat 8000:8000
kubectl rollout status -n serving deploy/churn
k9s
```

## Helm

```bash
helm template small-chat platform/charts/llm-model -f platform/gitops/llm-models/small-chat.yaml
helm -n observability list
helm -n observability get values kube-prometheus-stack
```

## Dagster / MLflow / data

```bash
uv run dagster dev -m mlops_course.pipelines.definitions
uv run python -m mlops_course.data.cli --out s3://datasets/churn --drift 0.5
uv run python -m mlops_course.training.train
uv run python -m mlops_course.training.registry show
uv run python -m mlops_course.training.registry promote
```

## LLM

```bash
platform/llm/run-tickets.sh 30 8
platform/observability/load-llm.sh 200 64
curl -s localhost:8000/v1/models
curl -s localhost:8000/metrics | grep vllm:
```

## GitOps / CI

```bash
kubectl -n argocd get applications
kubectl -n argocd logs -l app.kubernetes.io/name=argocd-application-controller --tail=50
# Gitea → Actions → ci → Run workflow   (workflow_dispatch)
```

## Prometheus / Grafana

```bash
# Grafana  admin / lab
# Prometheus → Status → Targets
# PromQL to paste:
#   sum by (model_name) (vllm:num_requests_waiting)
#   DCGM_FI_DEV_GPU_UTIL
#   histogram_quantile(0.95, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket[5m])))
```
