"""Tests for the synthetic data generator (written BEFORE the implementation).

Each test pins down one property the rest of the course relies on:
determinism, schema, drift behaviour and label sanity.
"""

from datetime import date

import polars as pl
import pytest

from mlops_course.data.churn import CHURN_SCHEMA, generate_customers
from mlops_course.data.config import GeneratorConfig
from mlops_course.data.tickets import INTENTS, generate_tickets


@pytest.fixture
def cfg() -> GeneratorConfig:
    return GeneratorConfig(n_customers=2_000, seed=7, snapshot_date=date(2026, 10, 1))


def test_same_seed_same_data(cfg: GeneratorConfig) -> None:
    # Reproducibility: re-running with the same config must give identical data,
    # otherwise DVC would see a "new" dataset on every run.
    assert generate_customers(cfg).equals(generate_customers(cfg))


def test_different_seed_different_data(cfg: GeneratorConfig) -> None:
    other = cfg.model_copy(update={"seed": 8})
    assert not generate_customers(cfg).equals(generate_customers(other))


def test_schema_is_stable(cfg: GeneratorConfig) -> None:
    df = generate_customers(cfg)
    assert dict(df.schema) == CHURN_SCHEMA
    assert df.height == cfg.n_customers
    assert df["customer_id"].is_unique().all()


def test_churn_rate_is_plausible(cfg: GeneratorConfig) -> None:
    rate = generate_customers(cfg)["churned"].mean()
    assert isinstance(rate, float)
    assert 0.10 < rate < 0.40


def test_churn_depends_on_tickets(cfg: GeneratorConfig) -> None:
    # The label must carry signal, or there is nothing for a model to learn.
    df = generate_customers(cfg)
    many = df.filter(pl.col("support_tickets_90d") >= 4)["churned"].mean()
    few = df.filter(pl.col("support_tickets_90d") <= 1)["churned"].mean()
    assert isinstance(many, float) and isinstance(few, float)
    assert many > few


def test_drift_shifts_distributions(cfg: GeneratorConfig) -> None:
    base = generate_customers(cfg)
    drifted = generate_customers(cfg.model_copy(update={"drift": 1.0}))
    assert drifted["monthly_spend"].mean() < base["monthly_spend"].mean()  # type: ignore[operator]
    assert drifted["support_tickets_90d"].mean() > base["support_tickets_90d"].mean()  # type: ignore[operator]


def test_drift_must_be_between_0_and_1() -> None:
    with pytest.raises(ValueError):
        GeneratorConfig(drift=1.5)


def test_tickets_have_known_intents(cfg: GeneratorConfig) -> None:
    tickets = generate_tickets(cfg, n=300)
    assert set(tickets["intent"].unique()) <= set(INTENTS)
    assert tickets["text"].str.len_chars().min() > 10  # type: ignore[operator]
    assert set(tickets["route"].unique()) <= {"small-chat", "big-reasoning"}
