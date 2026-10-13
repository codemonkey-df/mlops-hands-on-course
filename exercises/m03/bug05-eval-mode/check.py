"""Scoring the same rows twice must give the same probabilities."""
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import torch

from _pyload import fail, load
from mlops_course.data.churn import generate_customers
from mlops_course.data.config import GeneratorConfig
from mlops_course.training.features import Standardizer, to_matrix

model_mod = load(f"{sys.argv[1]}/model.py", "ex_model")
df = generate_customers(GeneratorConfig(n_customers=200, seed=5, snapshot_date=date(2026, 10, 1)))
with tempfile.TemporaryDirectory() as tmp:
    torch.manual_seed(0)
    net = model_mod.ChurnMLP(dropout=0.5)
    torch.save(net.state_dict(), f"{tmp}/w.pt")
    Path(f"{tmp}/s.json").write_text(json.dumps(Standardizer.fit(to_matrix(df)).to_dict()))
    ctx = SimpleNamespace(artifacts={"weights": f"{tmp}/w.pt", "scaler": f"{tmp}/s.json"},
                          model_config={"kind": "mlp", "hidden": 32})
    pyfunc = model_mod.ChurnPyfunc()
    pyfunc.load_context(ctx)
    pyfunc.model.net[2].p = 0.5  # make dropout obvious
    a = pyfunc.predict(None, df.to_pandas())["churn_probability"]
    b = pyfunc.predict(None, df.to_pandas())["churn_probability"]
if not a.equals(b):
    fail(f"predictions differ between calls (max diff {abs(a - b).max():.3f})")
print("OK")
