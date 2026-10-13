"""daily_churn() must return one row per snapshot day."""
import sys

from _pyload import fail, load
from mlops_course.data.config import S3Settings
from mlops_course.data.storage import duckdb_s3

queries = load(f"{sys.argv[1]}/queries.py", "ex_queries")
try:
    with duckdb_s3(S3Settings()) as con:
        rows = queries.daily_churn(con)
except Exception as exc:  # noqa: BLE001
    fail(f"{type(exc).__name__}: {str(exc)[:300]}")
if len(rows) < 2:
    fail(f"expected one row per day, got {rows}")
print("OK", rows)
