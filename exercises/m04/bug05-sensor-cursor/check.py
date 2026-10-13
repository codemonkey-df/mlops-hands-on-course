"""One drifted report -> exactly one run request, and nothing on the next tick."""
import sys

import dagster as dg

from _m04_helpers import local_env, materialize
from _pyload import fail, load
from mlops_course.pipelines import assets

auto = load(f"{sys.argv[1]}/automation.py", "ex_auto")
graph = [assets.raw_customers, assets.clean_customers, assets.reference_profile, assets.drift_report]
with local_env() as (instance, resources, _):
    for day, drift in (("2026-10-01", 0.0), ("2026-10-02", 1.0)):
        cfg = {"ops": {"raw_customers": {"config": {"drift": drift, "n_customers": 2000}}}}
        materialize(graph, instance, resources, ["raw_customers", "clean_customers"], day, cfg)
    materialize(graph, instance, resources, ["reference_profile"])
    materialize(graph, instance, resources, ["drift_report"], "2026-10-02")
    first = auto.drift_sensor(dg.build_sensor_context(instance=instance))
    second = auto.drift_sensor(dg.build_sensor_context(instance=instance, cursor=first.cursor))
print("tick1:", len(first.run_requests), "cursor:", first.cursor, "| tick2:", len(second.run_requests))
if len(first.run_requests) != 1:
    fail("first tick should request exactly one training run")
if second.run_requests:
    fail("second tick re-requested an already handled event: the cursor never advances")
print("OK")
