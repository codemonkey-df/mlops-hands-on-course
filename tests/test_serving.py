"""Unit tests for the serving logic (no BentoML server, no MLflow needed)."""

import pandas as pd
import pytest
from pydantic import ValidationError

from mlops_course.serving.predictor import ChurnPredictor, Customer, PredictRequest


class FakeModel:
    """Stands in for the MLflow pyfunc: records what it was called with."""

    def __init__(self) -> None:
        self.seen: pd.DataFrame | None = None

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        self.seen = df
        return pd.DataFrame(
            {"churn_probability": [0.9 if t > 3 else 0.1 for t in df["support_tickets_90d"]]}
        )


@pytest.fixture
def customer() -> dict[str, object]:
    return {
        "customer_id": "C000001",
        "plan": "basic",
        "region": "north",
        "tenure_months": 3,
        "monthly_spend": 19.9,
        "support_tickets_90d": 5,
        "days_since_last_order": 40,
        "app_sessions_30d": 2,
        "discount_used": False,
    }


def test_predict_returns_one_result_per_customer(customer: dict[str, object]) -> None:
    model = FakeModel()
    predictor = ChurnPredictor(model, model_version="7", threshold=0.5)
    req = PredictRequest(
        customers=[Customer(**customer), Customer(**{**customer, "support_tickets_90d": 0})]
    )

    resp = predictor.predict(req)

    assert [p.churn for p in resp.predictions] == [True, False]
    assert resp.predictions[0].customer_id == "C000001"
    assert resp.model_version == "7"


def test_model_receives_signature_dtypes(customer: dict[str, object]) -> None:
    model = FakeModel()
    ChurnPredictor(model, model_version="7").predict(
        PredictRequest(customers=[Customer(**customer)])
    )

    assert model.seen is not None
    assert "customer_id" not in model.seen.columns  # ids are not features
    assert model.seen["tenure_months"].dtype == "int32"  # MLflow signature says int32


def test_invalid_plan_is_rejected(customer: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Customer(**{**customer, "plan": "platinum"})


def test_empty_request_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PredictRequest(customers=[])
