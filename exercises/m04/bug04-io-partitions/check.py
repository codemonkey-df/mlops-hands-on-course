"""Two materialized days must stay two separate partitions in the lake."""
import sys

import polars as pl

from _m04_helpers import local_env, materialize
from _pyload import fail, load
from mlops_course.pipelines import assets
from mlops_course.pipelines.resources import S3Resource

io = load(f"{sys.argv[1]}/io_managers.py", "ex_io")
with local_env() as (instance, resources, tmp):
    lake = io.Lake(base_uri=f"{tmp}/lake2", s3=S3Resource(endpoint_url="x", access_key="x", secret_key="x"))
    resources = {**resources, "io_manager": io.PolarsParquetIOManager(lake=lake), "lake": lake}
    for day in ("2026-10-01", "2026-10-02"):
        r = materialize([assets.raw_customers], instance, resources, ["raw_customers"], day)
        if not r.success:
            fail("materialization failed")
    files = sorted(p.name for p in (tmp / "lake2" / "raw_customers").glob("*.parquet"))
    print("files:", files)
    if files != ["2026-10-01.parquet", "2026-10-02.parquet"]:
        fail(f"expected one file per partition, got {files}")
    day1 = pl.read_parquet(tmp / "lake2" / "raw_customers" / "2026-10-01.parquet")
    if str(day1["snapshot_date"][0]) != "2026-10-01":
        fail("partition 2026-10-01 contains another day's data")
print("OK")
