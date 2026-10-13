"""Shared helpers for the M4 exercises: local lake + temp MLflow + ephemeral instance."""

import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import dagster as dg

from mlops_course.pipelines.io_managers import Lake, PolarsParquetIOManager
from mlops_course.pipelines.resources import MLflowResource, S3Resource


@contextmanager
def local_env() -> Iterator[tuple[dg.DagsterInstance, dict[str, object], Path]]:
    with tempfile.TemporaryDirectory() as tmp, dg.DagsterInstance.ephemeral() as instance:
        s3 = S3Resource(endpoint_url="http://unused", access_key="x", secret_key="x")
        lake = Lake(base_uri=f"{tmp}/lake", s3=s3)
        resources = {
            "io_manager": PolarsParquetIOManager(lake=lake),
            "lake": lake,
            "mlflow_res": MLflowResource(tracking_uri=f"sqlite:///{tmp}/mlflow.db"),
        }
        yield instance, resources, Path(tmp)


def materialize(assets, instance, resources, selection, partition=None, run_config=None):  # type: ignore[no-untyped-def]
    return dg.materialize(
        assets,
        selection=selection,
        partition_key=partition,
        resources=resources,
        instance=instance,
        run_config=run_config,
        raise_on_error=False,
    )
