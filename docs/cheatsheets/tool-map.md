# Tool map (stub)

Short answers to “is X used here?” Elective paths (Spark, Slurm-style systems
work) are backlog items, not the default course line.

| Question | Short answer |
|----------|----------------|
| dlt used here? | No |
| DuckDB vs Postgres? | Analytics over Parquet (lake) vs platform metadata (MLflow, Dagster, LiteLLM) |
| BentoML vs Harbor? | Package/serve the model vs store container images |
| BentoML vs LLM proxy (LiteLLM)? | Custom model service vs gateway to many LLM backends |
| KServe for small always-on vLLM? | Often overkill in this lab — plain Deployments + KEDA |
| Slurm in MLOps? | Train/batch GPU farm; serving stays on Kubernetes here |
