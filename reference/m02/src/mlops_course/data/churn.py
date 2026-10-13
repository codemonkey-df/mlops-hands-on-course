"""Synthetic customer-churn table.

The data is generated from a known "ground truth" model, which is the big
advantage of synthetic data for learning: you know what the model SHOULD find,
and you can inject drift on purpose and watch monitoring/retraining react.
"""

import logging

import numpy as np
import polars as pl

from mlops_course.data.config import GeneratorConfig

logger = logging.getLogger(__name__)

PLANS = ["basic", "plus", "pro"]
REGIONS = ["north", "south", "east", "west"]

# The contract with every downstream consumer (features, training, serving).
# Tests assert it, so changing a column type is a deliberate, reviewed change.
CHURN_SCHEMA: dict[str, pl.DataType] = {
    "customer_id": pl.String(),
    "snapshot_date": pl.Date(),
    "plan": pl.String(),
    "region": pl.String(),
    "tenure_months": pl.Int32(),
    "monthly_spend": pl.Float64(),
    "support_tickets_90d": pl.Int32(),
    "days_since_last_order": pl.Int32(),
    "app_sessions_30d": pl.Int32(),
    "discount_used": pl.Boolean(),
    "churned": pl.Int8(),
}


def generate_customers(cfg: GeneratorConfig) -> pl.DataFrame:
    """Generate one snapshot of customers with a churn label.

    Args:
        cfg: Generation parameters (size, seed, drift, date).

    Returns:
        A DataFrame matching ``CHURN_SCHEMA``.
    """
    # One Generator object, seeded once. Never use np.random.* module functions:
    # they share hidden global state, so results depend on call order elsewhere.
    rng = np.random.default_rng(cfg.seed)
    n, d = cfg.n_customers, cfg.drift

    plan = rng.choice(PLANS, size=n, p=[0.55, 0.30, 0.15])
    region = rng.choice(REGIONS, size=n)
    tenure = rng.gamma(shape=2.0, scale=12.0, size=n).clip(1, 120).astype(np.int32)

    # Covariate drift: spend drops and tickets rise as drift -> 1.
    plan_base = np.select([plan == "basic", plan == "plus"], [25.0, 55.0], 95.0)
    spend = (plan_base * (1.0 - 0.35 * d) + rng.normal(0, 8, n)).clip(5, None)
    tickets = rng.poisson(lam=1.2 + 1.8 * d, size=n).astype(np.int32)
    last_order = rng.exponential(scale=20 + 25 * d, size=n).clip(0, 365).astype(np.int32)
    sessions = rng.poisson(lam=np.maximum(14 - 0.4 * tickets, 1)).astype(np.int32)
    discount = rng.random(n) < (0.2 + 0.3 * d)

    # Ground-truth churn model (log-odds). Concept drift: with drift the
    # discount effect flips sign (discount-hunters leave once promos end).
    logit = (
        -1.6
        + 0.45 * tickets
        + 0.025 * last_order
        - 0.03 * tenure
        - 0.08 * sessions
        + np.where(plan == "basic", 0.4, 0.0)
        + (0.6 * d - 0.3) * discount
    )
    churned = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(np.int8)

    df = pl.DataFrame(
        {
            "customer_id": [f"C{cfg.seed:03d}-{i:06d}" for i in range(n)],
            "snapshot_date": [cfg.snapshot_date] * n,
            "plan": plan,
            "region": region,
            "tenure_months": tenure,
            "monthly_spend": spend.round(2),
            "support_tickets_90d": tickets,
            "days_since_last_order": last_order,
            "app_sessions_30d": sessions,
            "discount_used": discount,
            "churned": churned,
        },
        schema=CHURN_SCHEMA,
    )
    logger.info("generated %d customers (drift=%.2f, churn rate=%.3f)", n, d, df["churned"].mean())
    return df
