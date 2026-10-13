"""Dagster tests: same assets, local IO manager + temp MLflow, ephemeral instance.

This is the payoff of resources/IO managers: no MinIO, no MLflow server, no
code changes. Only the injected resources differ.
"""

from pathlib import Path

import dagster as dg
import pytest

from mlops_course.pipelines import assets, training_assets
from mlops_course.pipelines.automation import drift_sensor
from mlops_course.pipelines.definitions import defs
from mlops_course.pipelines.io_managers import Lake, PolarsParquetIOManager
from mlops_course.pipelines.resources import MLflowResource, S3Resource

DAY1, DAY2 = "2026-10-01", "2026-10-02"


@pytest.fixture
def resources(tmp_path: Path) -> dict[str, object]:
    s3 = S3Resource(endpoint_url="http://unused", access_key="x", secret_key="x")
    lake = Lake(base_uri=str(tmp_path / "lake"), s3=s3)
    return {
        "io_manager": PolarsParquetIOManager(lake=lake),
        "lake": lake,
        "mlflow_res": MLflowResource(tracking_uri=f"sqlite:///{tmp_path}/mlflow.db"),
    }


def _materialize(instance, resources, selection, partition=None, run_config=None):  # type: ignore[no-untyped-def]
    return dg.materialize(
        dg.load_assets_from_modules([assets, training_assets]),
        selection=selection.split(),
        partition_key=partition,
        resources=resources,
        instance=instance,
        run_config=run_config,
    )


def test_definitions_load() -> None:
    # Catches missing resources, bad selections, typos in asset names, ...
    defs.resolve_all_job_defs()
    assert defs.resolve_job_def("training") is not None


def test_ingest_partition_and_checks(resources: dict[str, object]) -> None:
    with dg.DagsterInstance.ephemeral() as instance:
        result = _materialize(instance, resources, "raw_customers clean_customers", DAY1)
        assert result.success
        checks = result.get_asset_check_evaluations()
        assert {c.check_name for c in checks} == {"schema_matches", "churn_rate_plausible"}
        assert all(c.passed for c in checks)


def test_drift_sensor_triggers_once(resources: dict[str, object]) -> None:
    with dg.DagsterInstance.ephemeral() as instance:
        for day in (DAY1, DAY2):
            drift = 0.0 if day == DAY1 else 1.0
            cfg = {"ops": {"raw_customers": {"config": {"drift": drift, "n_customers": 3000}}}}
            assert _materialize(
                instance, resources, "raw_customers clean_customers", day, cfg
            ).success
        assert _materialize(instance, resources, "reference_profile").success
        assert _materialize(instance, resources, "drift_report", DAY2).success

        ctx = dg.build_sensor_context(instance=instance)
        first = drift_sensor(ctx)
        assert len(first.run_requests) == 1
        # Same events, advanced cursor -> nothing new to do.
        again = drift_sensor(dg.build_sensor_context(instance=instance, cursor=first.cursor))
        assert again.run_requests == []


def test_training_and_promotion(resources: dict[str, object]) -> None:
    with dg.DagsterInstance.ephemeral() as instance:
        for day in (DAY1, DAY2):
            assert _materialize(instance, resources, "raw_customers clean_customers", day).success
        result = _materialize(
            instance,
            resources,
            "churn_model champion_model",
            run_config={"ops": {"churn_model": {"config": {"epochs": 3, "model": "logreg"}}}},
        )
        assert result.success
        meta = result.asset_materializations_for_node("champion_model")[0].metadata
        assert meta["promoted"].value is True
