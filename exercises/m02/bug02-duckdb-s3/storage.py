"""Read/write datasets on MinIO (S3) with Polars and query them with DuckDB."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import duckdb
import polars as pl

from mlops_course.data.config import S3Settings

logger = logging.getLogger(__name__)


def write_partitioned(df: pl.DataFrame, uri: str, s3: S3Settings, partition_by: str) -> None:
    """Write a Hive-partitioned Parquet dataset.

    Result layout:  <uri>/snapshot_date=2026-10-01/<file>.parquet
    Query engines (DuckDB, Spark, Trino) understand the ``key=value`` folders
    and skip partitions that a WHERE clause excludes ("partition pruning").

    Args:
        df: Data to write.
        uri: Dataset root, e.g. ``s3://datasets/churn``.
        s3: Connection settings.
        partition_by: Column used for the folder structure.
    """
    options = s3.polars_options() if uri.startswith("s3://") else None
    df.write_parquet(uri, partition_by=partition_by, storage_options=options, mkdir=True)
    logger.info("wrote %d rows to %s (partitioned by %s)", df.height, uri, partition_by)


@contextmanager
def duckdb_s3(s3: S3Settings) -> Iterator[duckdb.DuckDBPyConnection]:
    """In-memory DuckDB connection that can read ``s3://`` paths on MinIO.

    Context manager: the connection is always closed, even on errors.

    Args:
        s3: Connection settings.

    Yields:
        A DuckDB connection with an S3 secret configured.
    """
    con = duckdb.connect()
    try:
        # httpfs is downloaded from extensions.duckdb.org on first use.
        # Fully offline? Pre-install it once: INSTALL httpfs; (cached in ~/.duckdb)
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute(
            """
            CREATE OR REPLACE SECRET minio (
                TYPE s3,
                KEY_ID $key,
                SECRET $secret,
                ENDPOINT $endpoint,
                REGION $region,
                USE_SSL false
            )
            """,
            {
                "key": s3.access_key,
                "secret": s3.secret_key,
                "endpoint": s3.endpoint_host(),
                "region": s3.region,
            },
        )
        yield con
    finally:
        con.close()
