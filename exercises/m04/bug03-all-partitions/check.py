"""With only 2 days materialized, training must still succeed."""
import sys

from _m04_helpers import local_env, materialize
from _pyload import fail, load
from mlops_course.pipelines import assets

mod = load(f"{sys.argv[1]}/training_assets.py", "ex_training")
all_assets = [assets.raw_customers, assets.clean_customers, mod.churn_model, mod.champion_model]
with local_env() as (instance, resources, _):
    for day in ("2026-10-01", "2026-10-02"):
        r = materialize(all_assets, instance, resources, ["raw_customers", "clean_customers"], day)
        assert r.success
    cfg = {"ops": {"churn_model": {"config": {"epochs": 2, "model": "logreg"}}}}
    r = materialize(all_assets, instance, resources, ["churn_model", "champion_model"], run_config=cfg)
    if not r.success:
        err = next(e for e in r.all_events if e.is_failure).event_specific_data.error  # type: ignore[union-attr]
        fail(f"training run failed: {err.message.strip()[:400]}")
print("OK")
