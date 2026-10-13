"""definitions.py must load and validate (what `dagster dev` does at startup)."""
import os
import sys

import dagster as dg

from _pyload import fail, load

for k in ("S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY", "MLFLOW_TRACKING_URI"):
    os.environ.setdefault(k, "x")
try:
    mod = load(f"{sys.argv[1]}/definitions.py", "ex_defs")
    dg.Definitions.validate_loadable(mod.defs)
except Exception as exc:  # noqa: BLE001
    fail(f"{type(exc).__name__}: {str(exc)[:400]}")
print("OK")
