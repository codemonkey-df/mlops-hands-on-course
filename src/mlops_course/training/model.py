"""Models and the MLflow pyfunc wrapper that bundles preprocessing."""

import json
from typing import Any

import mlflow
import numpy as np
import pandas as pd
import polars as pl
import torch
from torch import nn

from mlops_course.training.features import FEATURES, Standardizer, to_matrix


class ChurnMLP(nn.Module):
    """Small feed-forward network: features -> churn logit."""

    def __init__(self, n_features: int = len(FEATURES), hidden: int = 32, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),  # active in .train(), disabled in .eval()
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),  # raw logit; sigmoid is applied in the loss / at predict
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return one logit per row, shape (batch,)."""
        return self.net(x).squeeze(-1)


class ChurnPyfunc(mlflow.pyfunc.PythonModel):  # type: ignore[misc,name-defined]
    """What gets registered: RAW customer columns in, churn probability out.

    Artifacts (files logged with the model):
        weights: torch state_dict (.pt) OR a pickled sklearn model (.pkl)
        scaler:  Standardizer JSON
    """

    def load_context(self, context: Any) -> None:
        """Called once when the model is loaded (server start), not per request."""
        with open(context.artifacts["scaler"]) as fh:
            self.scaler = Standardizer.from_dict(json.load(fh))
        meta = context.model_config or {}
        self.kind = meta.get("kind", "mlp")
        self.model: Any
        if self.kind == "mlp":
            self.model = ChurnMLP(hidden=int(meta.get("hidden", 32)))
            self.model.load_state_dict(torch.load(context.artifacts["weights"]))
            self.model.eval()  # forget this and dropout makes predictions random
        else:
            import pickle

            with open(context.artifacts["weights"], "rb") as fh:
                self.model = pickle.load(fh)  # noqa: S301 - our own artifact

    def predict(self, context: Any, model_input: pd.DataFrame, params: Any = None) -> pd.DataFrame:
        """Score a batch of raw customer rows."""
        x = self.scaler.transform(to_matrix(pl.from_pandas(model_input)))
        if self.kind == "mlp":
            with torch.no_grad():
                proba = torch.sigmoid(self.model(torch.from_numpy(x))).numpy()
        else:
            proba = self.model.predict_proba(x)[:, 1]
        return pd.DataFrame({"churn_probability": np.asarray(proba, dtype=np.float64)})
