"""Framework-free serving logic: request/response schemas + the predictor.

Kept separate from the BentoML service so it can be unit-tested with a fake
model and reused by any server (BentoML, FastAPI, a batch job).
"""

from typing import Literal, Protocol

import pandas as pd
from pydantic import BaseModel, Field

# Columns (and dtypes) of the MLflow model signature logged in M3.
FEATURE_DTYPES: dict[str, str] = {
    "plan": "object",
    "region": "object",
    "tenure_months": "int32",
    "monthly_spend": "float64",
    "support_tickets_90d": "int32",
    "days_since_last_order": "int32",
    "app_sessions_30d": "int32",
    "discount_used": "bool",
}


class Customer(BaseModel):
    """One customer as sent by a client app (validated before the model sees it)."""

    customer_id: str
    plan: Literal["basic", "plus", "pro"]
    region: Literal["north", "south", "east", "west"]
    tenure_months: int = Field(ge=0)
    monthly_spend: float = Field(ge=0)
    support_tickets_90d: int = Field(ge=0)
    days_since_last_order: int = Field(ge=0)
    app_sessions_30d: int = Field(ge=0)
    discount_used: bool


class PredictRequest(BaseModel):
    """Batch of customers; bounded so one request cannot exhaust memory."""

    customers: list[Customer] = Field(min_length=1, max_length=1000)


class Prediction(BaseModel):
    """Score for one customer."""

    customer_id: str
    churn_probability: float
    churn: bool


class PredictResponse(BaseModel):
    """Scores plus the model version that produced them (for lineage/debugging)."""

    model_version: str
    predictions: list[Prediction]


class PyfuncLike(Protocol):
    """Anything with MLflow pyfunc's ``predict(DataFrame) -> DataFrame``."""

    def predict(self, df: pd.DataFrame) -> pd.DataFrame: ...


class ChurnPredictor:
    """Turns validated requests into model input and model output into responses.

    Args:
        model: Loaded pyfunc (or a fake in tests).
        model_version: Registry version, returned with every response.
        threshold: Probability above which ``churn`` is True.
    """

    def __init__(self, model: PyfuncLike, model_version: str, threshold: float = 0.5) -> None:
        self._model = model
        self.model_version = model_version
        self.threshold = threshold

    def predict(self, request: PredictRequest) -> PredictResponse:
        """Score a batch of customers."""
        rows = [c.model_dump() for c in request.customers]
        ids = [r.pop("customer_id") for r in rows]
        # pandas would infer int64; the MLflow signature enforces int32.
        features = pd.DataFrame(rows).astype(FEATURE_DTYPES)
        probs = self._model.predict(features)["churn_probability"].tolist()
        return PredictResponse(
            model_version=self.model_version,
            predictions=[
                Prediction(customer_id=i, churn_probability=float(p), churn=p >= self.threshold)
                for i, p in zip(ids, probs, strict=True)
            ],
        )
