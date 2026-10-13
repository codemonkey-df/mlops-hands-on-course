"""The single entry point Dagster loads: `dagster dev -m mlops_course.pipelines.definitions`.

Everything Dagster knows about lives in this one `Definitions` object. If an
asset, resource or sensor isn't listed (directly or via a job), it doesn't exist.
"""

import os

import dagster as dg

from mlops_course.pipelines import assets, training_assets
from mlops_course.pipelines.automation import (
    daily_ingest_job,
    daily_ingest_schedule,
    drift_sensor,
    training_job,
)
from mlops_course.pipelines.io_managers import Lake, PolarsParquetIOManager
from mlops_course.pipelines.resources import MLflowResource, S3Resource

# EnvVar is resolved when a run starts, so secrets never land in the Dagster DB.
s3 = S3Resource(
    endpoint_url=dg.EnvVar("S3_ENDPOINT_URL"),
    access_key=dg.EnvVar("S3_ACCESS_KEY"),
    secret_key=os.environ["S3_SECRET_KEY"],
)
lake = Lake(base_uri="s3://dagster", s3=s3)

defs = dg.Definitions(
    assets=dg.load_assets_from_modules([assets, training_assets]),
    jobs=[daily_ingest_job, training_job],
    schedules=[daily_ingest_schedule],
    sensors=[drift_sensor],
    resources={
        # "io_manager" is the default key used by every asset without io_manager_key.
        "io_manager": PolarsParquetIOManager(lake=lake),
        # Keys must match the asset parameter names (`lake: Lake`, `mlflow_res: ...`).
        "lake": lake,
        "mlflow_res": MLflowResource(tracking_uri=dg.EnvVar("MLFLOW_TRACKING_URI")),
    },
)
