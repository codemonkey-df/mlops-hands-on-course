"""Same config twice must give identical data."""
import sys
from datetime import date

from _pyload import fail, load
from mlops_course.data.config import GeneratorConfig

churn = load(f"{sys.argv[1]}/churn.py", "ex_churn")
cfg = GeneratorConfig(n_customers=500, seed=1, snapshot_date=date(2026, 10, 1))
a, b = churn.generate_customers(cfg), churn.generate_customers(cfg)
if not a.equals(b):
    diff = [c for c in a.columns if not a[c].equals(b[c])]
    fail(f"two runs with seed=1 differ in columns {diff}")
print("OK")
