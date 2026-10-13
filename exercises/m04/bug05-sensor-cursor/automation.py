"""Jobs, schedules and sensors: WHEN things run.

- daily_ingest_job + schedule: every night, materialize yesterday's partition.
- drift_sensor: when a drift_report shows drift, launch the training job.
"""

import dagster as dg

from mlops_course.pipelines.assets import PSI_ALERT
from mlops_course.pipelines.partitions import daily

# A job is a selection of assets to materialize together.
daily_ingest_job = dg.define_asset_job(
    "daily_ingest",
    selection=dg.AssetSelection.groups("ingest") | dg.AssetSelection.assets("drift_report"),
    partitions_def=daily,
)
training_job = dg.define_asset_job("training", selection=dg.AssetSelection.groups("training"))

# For a partitioned job, the schedule picks the partition automatically:
# the run at 01:30 on Oct 14 materializes partition 2026-10-13.
daily_ingest_schedule = dg.build_schedule_from_partitioned_job(
    daily_ingest_job, hour_of_day=1, minute_of_hour=30
)


@dg.sensor(job=training_job, minimum_interval_seconds=30)
def drift_sensor(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    """Request a training run for every NEW drift_report above the threshold.

    The cursor stores the last event id we looked at. Sensors are evaluated
    every 30 s; without the cursor we would re-trigger on the same old event
    forever (run_key dedups runs, but the sensor would still re-scan history).
    """
    after = int(context.cursor) if context.cursor else None
    records = context.instance.fetch_materializations(
        dg.AssetRecordsFilter(asset_key=dg.AssetKey("drift_report"), after_storage_id=after),
        limit=100,
        ascending=True,
    ).records

    run_requests = []
    for record in records:
        meta = record.asset_materialization.metadata if record.asset_materialization else {}
        max_psi = float(meta["max_psi"].value) if "max_psi" in meta else 0.0  # type: ignore[arg-type]
        if max_psi > PSI_ALERT:
            run_requests.append(
                dg.RunRequest(
                    run_key=f"drift-{record.storage_id}",  # idempotency key
                    tags={"trigger": "drift", "partition": str(record.partition_key)},
                )
            )
    return dg.SensorResult(run_requests=run_requests)
