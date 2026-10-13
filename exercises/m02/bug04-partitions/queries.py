"""Analytics queries over the partitioned churn dataset."""

import duckdb

CHURN = "s3://datasets/churn/*.parquet"


def daily_churn(con: duckdb.DuckDBPyConnection) -> list[tuple[object, ...]]:
    """Churn rate per snapshot day, oldest first."""
    return con.sql(
        f"""
        SELECT snapshot_date, count(*) AS customers, avg(churned) AS churn_rate
        FROM read_parquet('{CHURN}')
        GROUP BY snapshot_date
        ORDER BY snapshot_date
        """
    ).fetchall()
