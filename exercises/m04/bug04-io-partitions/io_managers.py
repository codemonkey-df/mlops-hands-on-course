"""The lake (where asset data lives) and the IO manager that uses it.

An IO manager decides WHERE and HOW asset values are stored. Assets just
`return df`; the IO manager writes it. Downstream assets just take `df` as a
parameter; the IO manager reads it. Swap the base URI (local folder in tests,
MinIO in prod) and no asset code changes.

Layout:
    <base_uri>/<asset_key>/<partition_key>.parquet   (partitioned assets)
    <base_uri>/<asset_key>/data.parquet              (unpartitioned assets)
"""

from pathlib import Path

import dagster as dg
import polars as pl

from mlops_course.data.storage import duckdb_s3
from mlops_course.pipelines.resources import S3Resource


class Lake(dg.ConfigurableResource):  # type: ignore[misc]
    """Location of asset data plus helpers to read it with Polars or DuckDB."""

    base_uri: str  # "s3://dagster" or a local directory
    s3: dg.ResourceDependency[S3Resource]

    @property
    def is_s3(self) -> bool:
        return self.base_uri.startswith("s3://")

    def options(self) -> dict[str, str] | None:
        """Polars storage options (None for local paths)."""
        return self.s3.settings().polars_options() if self.is_s3 else None

    def path(self, asset_key: dg.AssetKey, partition: str | None = None) -> str:
        """File of one asset (partition)."""
        name = f"{partition}.parquet" if partition else "data.parquet"
        return f"{self.base_uri}/{'/'.join(asset_key.path)}/{name}"

    def sql(self, query: str, **globs: str) -> pl.DataFrame:
        """Run DuckDB SQL; `{name}` placeholders become read_parquet(<all files of asset>).

        Example: lake.sql("SELECT count(*) FROM {t}", t="clean_customers")
        DuckDB reads only the files that EXIST: perfect for "whatever days we have".
        """
        tables = {
            k: f"read_parquet('{self.base_uri}/{v}/*.parquet', union_by_name = true)"
            for k, v in globs.items()
        }
        if self.is_s3:
            with duckdb_s3(self.s3.settings()) as con:
                return con.sql(query.format(**tables)).pl()
        import duckdb

        with duckdb.connect() as con:
            return con.sql(query.format(**tables)).pl()


class PolarsParquetIOManager(dg.ConfigurableIOManager):  # type: ignore[misc]
    """Stores Polars DataFrames as Parquet files in the lake."""

    lake: dg.ResourceDependency[Lake]

    def handle_output(self, context: dg.OutputContext, obj: pl.DataFrame) -> None:
        """Called after an asset returns. One file per partition."""
        path = self.lake.path(context.asset_key)
        if not self.lake.is_s3:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        obj.write_parquet(path, storage_options=self.lake.options())
        # Metadata shows up in the UI on the materialization (and can be plotted).
        context.add_output_metadata({"rows": obj.height, "path": path})

    def load_input(self, context: dg.InputContext) -> pl.DataFrame:
        """Called before a downstream asset runs.

        If the upstream asset is partitioned, Dagster tells us WHICH partitions
        the downstream needs (decided by the partition mapping). Note: an
        UNpartitioned downstream of a partitioned upstream asks for ALL
        partitions, materialized or not.
        """
        if context.has_asset_partitions:
            frames = [
                pl.read_parquet(
                    self.lake.path(context.asset_key, k), storage_options=self.lake.options()
                )
                for k in context.asset_partition_keys
            ]
            context.log.info(
                f"loaded {len(frames)} partition(s) of {context.asset_key.to_user_string()}"
            )
            return pl.concat(frames)
        return pl.read_parquet(
            self.lake.path(context.asset_key), storage_options=self.lake.options()
        )
