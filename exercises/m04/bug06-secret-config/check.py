"""Secrets must stay EnvVar references, never plain values in resource config."""
import os
import sys

import dagster as dg

from _pyload import fail, load

for k in ("S3_ENDPOINT_URL", "S3_ACCESS_KEY", "MLFLOW_TRACKING_URI"):
    os.environ.setdefault(k, "x")
os.environ["S3_SECRET_KEY"] = "super-secret-value"
mod = load(f"{sys.argv[1]}/definitions.py", "ex_defs6")
secret = mod.s3.secret_key
print("S3Resource.secret_key =", repr(secret))
if not isinstance(secret, dg.EnvVar):
    fail("the secret was read at import time: it is now visible in the UI and run storage")
print("OK")
