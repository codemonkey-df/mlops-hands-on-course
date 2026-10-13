"""Polars must write and read back a Parquet file on MinIO."""
import sys

import polars as pl

from _pyload import fail, load

config = load(f"{sys.argv[1]}/config.py", "ex_config")
opts = config.S3Settings().polars_options()
uri = "s3://datasets/exercises/m02-bug03.parquet"
try:
    pl.DataFrame({"x": [1, 2, 3]}).write_parquet(uri, storage_options=opts)
    back = pl.read_parquet(uri, storage_options=opts)
except Exception as exc:  # noqa: BLE001
    fail(f"{type(exc).__name__}: {str(exc)[:300]}")
assert back["x"].to_list() == [1, 2, 3]
print("OK")
