"""The asset graph built from assets.py must be a DAG (what `dagster dev` checks at load)."""
import sys

import dagster as dg

from _m04_helpers import local_env
from _pyload import fail, load
from mlops_course.pipelines import training_assets

try:
    mod = load(f"{sys.argv[1]}/assets.py", "ex_assets")
    with local_env() as (_, resources, _tmp):
        defs = dg.Definitions(
            assets=dg.load_assets_from_modules([mod, training_assets]), resources=resources
        )
        dg.Definitions.validate_loadable(defs)
except Exception as exc:  # noqa: BLE001
    fail(f"{type(exc).__name__}: {str(exc)[:400]}")
print("OK")
