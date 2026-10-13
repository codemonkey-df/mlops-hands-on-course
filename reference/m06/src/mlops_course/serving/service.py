"""BentoML service: HTTP API around ChurnPredictor.

Run locally:   uv run bentoml serve mlops_course.serving.service:ChurnService
Endpoints:     POST /predict   GET /model_info   GET /metrics   GET /readyz /livez
"""

import logging
from typing import Any

import bentoml
from prometheus_client import Histogram

from mlops_course.serving.predictor import ChurnPredictor, PredictRequest, PredictResponse

logger = logging.getLogger(__name__)

# Custom business metric next to BentoML's built-in request metrics. The score
# distribution shifting is often the first visible sign of data drift.
CHURN_SCORE = Histogram(
    "churn_prediction_probability",
    "Predicted churn probability per customer",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)


@bentoml.service(
    name="churn",
    workers=2,  # processes; each loads its own copy of the model
    traffic={"timeout": 10, "max_concurrency": 32},  # extra requests queue -> 503
    metrics={"enabled": True, "namespace": "bentoml_service"},
)
class ChurnService:
    """Churn scoring API. The model is baked into the Bento at build time."""

    # Resolved when the Bento is BUILT ("latest" = newest in the local store),
    # then frozen: the image always contains exactly this model version.
    model_ref = bentoml.models.BentoModel("churn-classifier:latest")

    def __init__(self) -> None:
        model = bentoml.mlflow.load_model(self.model_ref)
        version = self.model_ref.info.labels.get("mlflow_version", "unknown")
        self.predictor = ChurnPredictor(model, model_version=version)
        logger.info("loaded %s (mlflow v%s)", self.model_ref.tag, version)

    @bentoml.api
    def predict(self, request: PredictRequest) -> PredictResponse:
        """Score a batch of customers."""
        response = self.predictor.predict(request)
        for p in response.predictions:
            CHURN_SCORE.observe(p.churn_probability)
        return response

    @bentoml.api(route="/model_info")
    def model_info(self) -> dict[str, Any]:
        """Which model is this pod serving?"""
        return {
            "bento_model": str(self.model_ref.tag),
            "labels": self.model_ref.info.labels,
            "metadata": self.model_ref.info.metadata,
        }
