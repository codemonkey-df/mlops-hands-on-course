"""Ingestion and monitoring assets.

Asset graph (this file):

    raw_customers[day] -> clean_customers[day] -> drift_report[day]
                                \\-> reference_profile --/
"""

from datetime import date

import dagster as dg
import numpy as np
import polars as pl

from mlops_course.data.churn import CHURN_SCHEMA, generate_customers
from mlops_course.data.config import GeneratorConfig
from mlops_course.pipelines.partitions import START_DATE, daily

MONITORED = ["monthly_spend", "support_tickets_90d", "days_since_last_order"]
PSI_ALERT = 0.2  # rule of thumb: <0.1 stable, 0.1-0.2 moderate, >0.2 significant shift


class RawDataConfig(dg.Config):  # type: ignore[misc]
    """Run config: editable in the Launchpad before launching a run."""

    n_customers: int = 10_000
    drift: float = 0.0
    seed: int = 42


@dg.asset(partitions_def=daily, group_name="ingest", kinds={"polars"})
def raw_customers(context: dg.AssetExecutionContext, config: RawDataConfig) -> pl.DataFrame:
    """One day of customer snapshots, as delivered by the (synthetic) source system."""
    day = date.fromisoformat(context.partition_key)
    # Seed derived from the partition: re-materializing a day is reproducible.
    seed = config.seed + (day - date.fromisoformat(START_DATE)).days
    cfg = GeneratorConfig(
        n_customers=config.n_customers, seed=seed, drift=config.drift, snapshot_date=day
    )
    return generate_customers(cfg)


@dg.asset(
    partitions_def=daily,
    group_name="ingest",
    kinds={"polars"},
    # Checks declared on the asset and emitted from inside it. They run with
    # every materialization; a failing ERROR-severity check marks the run red.
    check_specs=[
        dg.AssetCheckSpec("schema_matches", asset="clean_customers"),
        dg.AssetCheckSpec("churn_rate_plausible", asset="clean_customers"),
    ],
)
def clean_customers(raw_customers: pl.DataFrame) -> dg.Output[pl.DataFrame]:  # type: ignore[misc]
    """Deduplicated, validated customers. The contract for everything downstream."""
    df = raw_customers.unique(subset=["customer_id"], keep="last").filter(
        pl.col("monthly_spend") > 0, pl.col("tenure_months") >= 0
    )
    churn_rate = float(df["churned"].mean())  # type: ignore[arg-type]
    yield dg.Output(df, metadata={"rows": df.height, "churn_rate": churn_rate})
    yield dg.AssetCheckResult(
        check_name="schema_matches",
        passed=dict(df.schema) == CHURN_SCHEMA,
        metadata={"columns": list(df.columns)},
    )
    yield dg.AssetCheckResult(
        check_name="churn_rate_plausible",
        passed=0.02 <= churn_rate <= 0.6,
        metadata={"churn_rate": churn_rate},
    )


@dg.asset(
    group_name="monitoring",
    # refresh the reference profile whenever a new drift report exists
    deps=["drift_report"],
    ins={
        # Partition mapping: this unpartitioned asset reads ONE fixed partition
        # of the partitioned upstream: the first day is our reference world.
        "clean_customers": dg.AssetIn(
            partition_mapping=dg.SpecificPartitionsPartitionMapping([START_DATE])
        )
    },
)
def reference_profile(clean_customers: pl.DataFrame) -> pl.DataFrame:
    """Decile bin edges + shares of the monitored columns on the reference day."""
    rows = []
    for col in MONITORED:
        values = clean_customers[col].to_numpy().astype(float)
        edges = np.unique(np.quantile(values, np.linspace(0, 1, 11)))
        counts, _ = np.histogram(values, bins=edges)
        for i, count in enumerate(counts):
            rows.append(
                {
                    "feature": col,
                    "bin": i,
                    "lower": edges[i],
                    "upper": edges[i + 1],
                    "ref_share": count / len(values),
                }
            )
    return pl.DataFrame(rows)


def psi(ref_share: np.ndarray, cur_share: np.ndarray, eps: float = 1e-4) -> float:
    """Population Stability Index between two binned distributions."""
    ref, cur = np.clip(ref_share, eps, None), np.clip(cur_share, eps, None)
    return float(np.sum((cur - ref) * np.log(cur / ref)))


@dg.asset(partitions_def=daily, group_name="monitoring")
def drift_report(
    context: dg.AssetExecutionContext,
    clean_customers: pl.DataFrame,
    reference_profile: pl.DataFrame,
) -> pl.DataFrame:
    """PSI per monitored feature for one day vs the reference day."""
    rows = []
    for col in MONITORED:
        prof = reference_profile.filter(pl.col("feature") == col).sort("bin")
        edges = np.append(prof["lower"].to_numpy(), prof["upper"].to_numpy()[-1])
        edges[0], edges[-1] = -np.inf, np.inf  # catch values outside the reference range
        counts, _ = np.histogram(clean_customers[col].to_numpy().astype(float), bins=edges)
        rows.append(
            {"feature": col, "psi": psi(prof["ref_share"].to_numpy(), counts / counts.sum())}
        )
    report = pl.DataFrame(rows)
    max_psi = float(report["psi"].max())  # type: ignore[arg-type]
    # The sensor reads this metadata to decide whether to retrain.
    context.add_output_metadata({"max_psi": max_psi, "drifted": max_psi > PSI_ALERT})
    return report
