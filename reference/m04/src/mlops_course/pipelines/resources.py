"""Resources = the external systems assets talk to, injected by Dagster.

Why not just read env vars inside assets?
  - Dependency injection: tests pass a fake/local resource, prod passes the real one.
  - Config is visible (and validated) in the UI under Deployment > Resources.
  - Secrets come from `dg.EnvVar("...")`: resolved at run time, never stored
    in the Dagster database or shown in the UI.
"""

import os

import dagster as dg
import mlflow

from mlops_course.data.config import S3Settings


class S3Resource(dg.ConfigurableResource):  # type: ignore[misc]
    """MinIO / S3 connection settings."""

    endpoint_url: str
    access_key: str
    secret_key: str
    region: str = "us-east-1"

    def settings(self) -> S3Settings:
        """Bridge to the M2 settings object, so Polars/DuckDB helpers are reused."""
        return S3Settings(
            endpoint_url=self.endpoint_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            region=self.region,
        )


class MLflowResource(dg.ConfigurableResource):  # type: ignore[misc]
    """Points the MLflow client at the tracking server for the duration of a run."""

    tracking_uri: str
    # Outside the cluster the presigned multipart URLs aren't reachable (see M3).
    disable_multipart: bool = True

    def setup_for_execution(self, context: dg.InitResourceContext) -> None:
        """Runs once per run (per step process), before any asset executes."""
        mlflow.set_tracking_uri(self.tracking_uri)
        if self.disable_multipart:
            os.environ["MLFLOW_ENABLE_PROXY_MULTIPART_DOWNLOAD"] = "false"
            os.environ["MLFLOW_ENABLE_PROXY_MULTIPART_UPLOAD"] = "false"
        if context.log:
            context.log.info(f"MLflow tracking URI: {self.tracking_uri}")
