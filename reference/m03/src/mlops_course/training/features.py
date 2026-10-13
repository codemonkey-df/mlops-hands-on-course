"""Feature engineering shared by training AND serving.

Training/serving skew (features computed differently in the two places) is
one of the most common silent ML bugs. The cure: one function, `to_matrix`,
used by both, and preprocessing state (mean/std) shipped inside the model.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
import polars as pl

NUMERIC = [
    "tenure_months",
    "monthly_spend",
    "support_tickets_90d",
    "days_since_last_order",
    "app_sessions_30d",
]
PLANS = ["basic", "plus", "pro"]
REGIONS = ["north", "south", "east", "west"]

FEATURES = (
    NUMERIC + ["discount_used"] + [f"plan_{p}" for p in PLANS] + [f"region_{r}" for r in REGIONS]
)
LABEL = "churned"


def build_features(df: pl.DataFrame) -> pl.DataFrame:
    """Turn raw customer columns into model features (lazy-friendly Polars).

    One-hot encoding is done against FIXED category lists: if a snapshot
    happens to contain no "pro" customers, the column still exists.
    """
    return df.select(
        *[pl.col(c).cast(pl.Float32) for c in NUMERIC],
        pl.col("discount_used").cast(pl.Float32),
        *[(pl.col("plan") == p).cast(pl.Float32).alias(f"plan_{p}") for p in PLANS],
        *[(pl.col("region") == r).cast(pl.Float32).alias(f"region_{r}") for r in REGIONS],
    )


def to_matrix(df: pl.DataFrame) -> np.ndarray:
    """Raw customers -> float32 matrix with columns in FEATURES order."""
    return build_features(df).select(FEATURES).to_numpy().astype(np.float32)


@dataclass
class Standardizer:
    """Zero-mean / unit-variance scaling with statistics frozen at fit time."""

    mean: np.ndarray
    std: np.ndarray

    @classmethod
    def fit(cls, x: np.ndarray) -> "Standardizer":
        """Learn mean/std from TRAINING data only (fitting on all data leaks)."""
        std = x.std(axis=0)
        return cls(mean=x.mean(axis=0), std=np.where(std == 0, 1.0, std))

    def transform(self, x: np.ndarray) -> np.ndarray:
        """Apply the frozen statistics."""
        return ((x - self.mean) / self.std).astype(np.float32)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable form, stored next to the model weights."""
        return {"mean": self.mean.tolist(), "std": self.std.tolist(), "features": FEATURES}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Standardizer":
        """Inverse of to_dict; refuses stats computed for different features."""
        if data["features"] != FEATURES:
            raise ValueError("scaler was fitted on a different feature list")
        return cls(mean=np.array(data["mean"]), std=np.array(data["std"]))
