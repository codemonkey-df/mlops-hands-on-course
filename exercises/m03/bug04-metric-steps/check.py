"""The loss history must have one point per epoch at steps 0..n-1."""
import sys
import tempfile

import mlflow
from mlflow import MlflowClient

from _pyload import fail, load

loop = load(f"{sys.argv[1]}/loop.py", "ex_loop")
with tempfile.TemporaryDirectory() as tmp:
    mlflow.set_tracking_uri(f"sqlite:///{tmp}/m.db")
    with mlflow.start_run() as run:
        loop.train_loop(5)
    hist = MlflowClient().get_metric_history(run.info.run_id, "train_loss")
steps = sorted(m.step for m in hist)
print("steps:", steps)
if steps != [0, 1, 2, 3, 4]:
    fail(f"expected steps [0..4], got {steps}: the UI cannot draw a curve")
print("OK")
