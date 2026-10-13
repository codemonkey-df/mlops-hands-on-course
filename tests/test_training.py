"""Tests for features + training. MLflow writes to a temp SQLite store, so the
tests never touch the shared tracking server."""

from datetime import date
from pathlib import Path

import mlflow
import numpy as np
import polars as pl
import pytest

from mlops_course.data.churn import generate_customers
from mlops_course.data.config import GeneratorConfig
from mlops_course.training.features import FEATURES, Standardizer, to_matrix
from mlops_course.training.train import TrainConfig, train


@pytest.fixture
def customers() -> pl.DataFrame:
    return generate_customers(
        GeneratorConfig(n_customers=3_000, seed=3, snapshot_date=date(2026, 10, 1))
    )


@pytest.fixture
def local_mlflow(tmp_path: Path) -> str:
    uri = f"sqlite:///{tmp_path}/mlflow.db"
    mlflow.set_tracking_uri(uri)
    return uri


def test_feature_matrix_shape_and_dtype(customers: pl.DataFrame) -> None:
    x = to_matrix(customers)
    assert x.shape == (customers.height, len(FEATURES))
    assert x.dtype == np.float32
    assert not np.isnan(x).any()


def test_standardizer_uses_train_statistics_only(customers: pl.DataFrame) -> None:
    x = to_matrix(customers)
    scaler = Standardizer.fit(x[:1000])
    z = scaler.transform(x[:1000])
    np.testing.assert_allclose(z.mean(axis=0), 0, atol=1e-5)
    # Transforming other rows must reuse the SAME mean/std (no re-fitting).
    assert scaler.transform(x[1000:]).mean() != pytest.approx(0, abs=1e-6)


def test_standardizer_roundtrips_through_json(customers: pl.DataFrame) -> None:
    scaler = Standardizer.fit(to_matrix(customers))
    again = Standardizer.from_dict(scaler.to_dict())
    np.testing.assert_array_equal(scaler.mean, again.mean)


@pytest.mark.parametrize("kind", ["logreg", "mlp"])
def test_training_beats_random_and_logs_model(
    customers: pl.DataFrame, local_mlflow: str, kind: str
) -> None:
    result = train(customers, TrainConfig(model=kind, epochs=15, experiment="test"))
    assert result.metrics["val_auc"] > 0.70
    model = mlflow.pyfunc.load_model(result.model_uri)
    # The logged model takes RAW columns: preprocessing travels with it.
    preds = model.predict(customers.head(5).to_pandas())
    assert len(preds) == 5
    assert ((preds["churn_probability"] >= 0) & (preds["churn_probability"] <= 1)).all()
