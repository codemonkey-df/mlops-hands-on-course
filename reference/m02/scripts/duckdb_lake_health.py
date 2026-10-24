"""One-shot DuckDB lake health query (avoids REPL multi-line paste indent errors)."""

from __future__ import annotations

from mlops_course.data.config import S3Settings
from mlops_course.data.storage import duckdb_s3


def main() -> None:
    """Print snapshot counts and churn by plan from s3://datasets/churn."""
    with duckdb_s3(S3Settings()) as con:
        print(
            con.sql(
                """
                SELECT snapshot_date, count(*) n, round(avg(churned), 3) churn_rate
                FROM read_parquet(
                    's3://datasets/churn/*/*.parquet',
                    hive_partitioning = true
                )
                GROUP BY ALL
                ORDER BY 1
                """
            )
        )
        print(
            con.sql(
                """
                SELECT plan, round(avg(churned), 3)
                FROM 's3://datasets/churn/*/*.parquet'
                GROUP BY 1
                """
            )
        )


if __name__ == "__main__":
    main()
