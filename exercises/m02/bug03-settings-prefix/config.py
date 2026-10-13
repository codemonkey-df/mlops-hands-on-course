"""Validated configuration for data generation and S3 access.

Pydantic validates values at construction time, so a typo in params.yaml
(e.g. drift: 1.5) fails immediately with a clear message instead of
silently producing nonsense data.
"""

from datetime import date

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneratorConfig(BaseModel):
    """Parameters of one synthetic snapshot.

    Attributes:
        n_customers: Number of customer rows to generate.
        seed: Random seed. Same seed + same config = byte-identical data.
        drift: 0.0 = reference world, 1.0 = maximally shifted world
            (cheaper customers, more support tickets, different churn drivers).
        snapshot_date: Business date of the snapshot, used as partition key.
    """

    n_customers: int = Field(default=10_000, gt=0)
    seed: int = 42
    drift: float = Field(default=0.0, ge=0.0, le=1.0)
    snapshot_date: date = date(2026, 10, 1)


class S3Settings(BaseSettings):
    """S3/MinIO connection, read from environment variables (or `.env`).

    Never hard-code credentials: S3_ACCESS_KEY / S3_SECRET_KEY come from the
    environment, which in Kubernetes is filled from a Secret.
    """

    model_config = SettingsConfigDict(env_prefix="S3", env_file=".env", extra="ignore")

    endpoint_url: str = "http://s3.192.168.1.202.nip.io:8080"
    access_key: str = "mlops"
    secret_key: str = ""
    region: str = "us-east-1"  # MinIO ignores it, but every S3 client wants one

    def polars_options(self) -> dict[str, str]:
        """Storage options in the format Polars' object_store backend expects."""
        return {
            "aws_endpoint_url": self.endpoint_url,
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "aws_region": self.region,
            "aws_allow_http": "true",  # plain HTTP is refused by default
        }

    def endpoint_host(self) -> str:
        """Endpoint without scheme, the format DuckDB's ENDPOINT expects."""
        return self.endpoint_url.split("://", 1)[-1]
