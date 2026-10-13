"""DuckDB must read the churn dataset from MinIO (needs M1 + data from M2 step 3)."""
import sys

from _pyload import fail, load
from mlops_course.data.config import S3Settings

storage = load(f"{sys.argv[1]}/storage.py", "ex_storage")
try:
    with storage.duckdb_s3(S3Settings()) as con:
        n = con.sql("SELECT count(*) FROM 's3://datasets/churn/*/*.parquet'").fetchone()[0]
except Exception as exc:  # noqa: BLE001 - we want to show any failure
    fail(f"{type(exc).__name__}: {exc}")
print(f"OK ({n} rows)")
