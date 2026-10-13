# MLflow tracking server image = official image + the two drivers it lacks.
#   psycopg -> Postgres backend store (runs, params, metrics, registry)
#   boto3   -> S3/MinIO artifact store (models, plots, files)
# The official `-full` tag has them too but is ~300 MB bigger (all ML flavors).
FROM ghcr.io/mlflow/mlflow:v3.17.1

# SQLAlchemy 2.1 maps `postgresql://` to psycopg 3 (`psycopg`), not psycopg2.
# We install psycopg 3 and spell the driver out in the URI anyway:
#   postgresql+psycopg://user:pass@host/db
# --no-cache-dir: don't keep pip's download cache inside the image layer.
RUN pip install --no-cache-dir "psycopg[binary]==3.3.6" boto3==1.43.112

# Document the port; it does not publish anything by itself.
EXPOSE 5000

# Run as non-root. Kubernetes can enforce it with `runAsNonRoot: true`.
USER 1000
