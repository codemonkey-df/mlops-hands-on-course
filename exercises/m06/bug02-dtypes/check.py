"""ChurnPredictor must work with the REAL model (signature enforcement on)."""
import logging
import sys

import bentoml

from _pyload import fail, load

logging.disable(logging.WARNING)
mod = load(f"{sys.argv[1]}/predictor.py", "ex_predictor")
model = bentoml.mlflow.load_model("churn-classifier:latest")
req = mod.PredictRequest(customers=[mod.Customer(
    customer_id="C1", plan="basic", region="north", tenure_months=2, monthly_spend=15.0,
    support_tickets_90d=6, days_since_last_order=60, app_sessions_30d=1, discount_used=False)])
try:
    resp = mod.ChurnPredictor(model, model_version="x").predict(req)
except Exception as exc:  # noqa: BLE001
    fail(f"{type(exc).__name__}: {str(exc)[:300]}")
print(resp)
print("OK")
