"""Training and promotion assets (reuse the M3 code unchanged).

    clean_customers[days in lake] ..> churn_model ..> champion_model
    clean_customers[newest day]   ....................^

`..>` = `deps`: an ordering/lineage edge WITHOUT the IO manager loading data.
churn_model queries the lake itself with DuckDB, reading only the files that
exist and only the window it needs.
"""

import dagster as dg
import mlflow
import polars as pl

from mlops_course.pipelines.io_managers import Lake
from mlops_course.pipelines.resources import MLflowResource
from mlops_course.training.registry import CHAMPION, MODEL_NAME, promote, register
from mlops_course.training.train import TrainConfig, train


class TrainingConfig(dg.Config):  # type: ignore[misc]
    """Hyper-parameters exposed in the Launchpad."""

    model: str = "mlp"
    epochs: int = 15
    window_days: int = 7  # train on the most recent N days only


@dg.asset(group_name="training", kinds={"pytorch", "mlflow"})
def churn_model(
    context: dg.AssetExecutionContext,
    config: TrainingConfig,
    mlflow_res: MLflowResource,
    clean_customers: pl.DataFrame,  # let the IO manager load the training data
) -> dg.MaterializeResult:  # type: ignore[type-arg]
    """Train on the most recent window, log to MLflow, register as @challenger."""
    newest = clean_customers["snapshot_date"].max()
    window = clean_customers.filter(
        pl.col("snapshot_date") > pl.lit(newest) - pl.duration(days=config.window_days)
    )
    days = sorted({str(d) for d in window["snapshot_date"].unique()})
    context.log.info(f"training on {window.height} rows from {len(days)} day(s)")
    result = train(
        window,
        TrainConfig(
            model=config.model,  # type: ignore[arg-type]
            epochs=config.epochs,
            data_version=f"{days[0]}..{days[-1]}",
        ),
    )
    version = register(result.run_id)
    experiment_id = mlflow.get_run(result.run_id).info.experiment_id
    return dg.MaterializeResult(
        metadata={
            "run_id": result.run_id,
            "model_version": version,
            "val_auc": result.metrics["val_auc"],
            "train_days": len(days),
            "mlflow_run": dg.MetadataValue.url(
                f"{mlflow_res.tracking_uri}/#/experiments/{experiment_id}/runs/{result.run_id}"
            ),
        }
    )


@dg.asset(group_name="training", kinds={"mlflow"}, deps=[churn_model, "clean_customers"])
def champion_model(
    context: dg.AssetExecutionContext, mlflow_res: MLflowResource, lake: Lake
) -> dg.MaterializeResult:  # type: ignore[type-arg]
    """Promote @challenger to @champion if it wins on the newest day in the lake.

    Not `AssetIn(partition_mapping=LastPartitionMapping())`: that means the last
    partition of the DEFINITION (yesterday), which may never have been materialized.
    """
    holdout: pl.DataFrame = lake.sql(
        "SELECT * FROM {t} WHERE snapshot_date = (SELECT max(snapshot_date) FROM {t})",
        t="clean_customers",
    )
    decision = promote(holdout, min_gain=0.0)
    context.log.info(f"{MODEL_NAME}@{CHAMPION}: {decision}")
    champion = decision.challenger_version if decision.promoted else decision.champion_version
    return dg.MaterializeResult(
        metadata={
            "promoted": decision.promoted,
            "champion_version": str(champion),
            "challenger_auc": decision.challenger_auc,
            "champion_auc": decision.champion_auc or 0.0,
        }
    )
