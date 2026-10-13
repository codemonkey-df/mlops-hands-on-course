# On-prem MLOps hands-on course

A 12-module course that builds a complete on-prem MLOps platform on a k3d
Kubernetes cluster inside this LXC: Dagster, MLflow, DVC, MinIO, Postgres,
BentoML, mocked vLLM + LiteLLM router, Gitea CI, Harbor, ArgoCD, KEDA,
Prometheus and Grafana.

## Start the course site

```bash
make docs            # http://<LXC-IP>:8000  (live reload)
```

Everything else (cluster, tools, modules) is explained on the site.

## Layout

| Path | What lives there |
|------|------------------|
| `docs/` | The course pages (MkDocs Material) |
| `reference/mNN/` | Verified reference code, embedded in the pages |
| `src/mlops_course/`, `platform/`, `infra/` | **Your** implementation |
| `exercises/mNN/` | Planted-bug variants + `make check-mNN` verifiers |
