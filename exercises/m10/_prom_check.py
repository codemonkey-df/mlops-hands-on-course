"""Static checks for M10 ServiceMonitor / ScaledObject YAML.

Usage: python _prom_check.py <file.yaml> <check-name>
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

RELEASE = "kube-prometheus-stack"
WAITING = "vllm:num_requests_waiting"


def load(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        sys.exit("FAIL: file is not a YAML mapping")
    return data


def check_servicemonitor(doc: dict) -> None:
    if doc.get("kind") != "ServiceMonitor":
        sys.exit("FAIL: kind must be ServiceMonitor")
    labels = (doc.get("metadata") or {}).get("labels") or {}
    if labels.get("release") != RELEASE:
        sys.exit(
            f"FAIL: metadata.labels.release is {labels.get('release')!r}; "
            f"Prometheus only scrapes ServiceMonitors labelled release={RELEASE}"
        )
    endpoints = (doc.get("spec") or {}).get("endpoints") or []
    if not endpoints:
        sys.exit("FAIL: spec.endpoints is empty")
    ports = {e.get("port") for e in endpoints}
    if "http" not in ports:
        sys.exit(f"FAIL: no endpoint scrapes port 'http' (got {ports})")
    selector = ((doc.get("spec") or {}).get("selector") or {}).get("matchLabels") or {}
    if not selector:
        sys.exit("FAIL: spec.selector.matchLabels is empty — matches nothing")


def check_query(doc: dict) -> None:
    if doc.get("kind") != "ScaledObject":
        sys.exit("FAIL: kind must be ScaledObject")
    triggers = (doc.get("spec") or {}).get("triggers") or []
    if not triggers:
        sys.exit("FAIL: no triggers")
    t = triggers[0]
    if t.get("type") != "prometheus":
        sys.exit("FAIL: trigger type must be prometheus")
    if t.get("metricType") != "Value":
        sys.exit(
            f"FAIL: metricType is {t.get('metricType')!r}; queue depth must be "
            "Value (AverageValue divides by replica count and may never scale)"
        )
    query = (t.get("metadata") or {}).get("query") or ""
    if WAITING not in query:
        sys.exit(
            f"FAIL: query {query!r} does not use {WAITING!r} "
            "(the colon is part of the vLLM name; underscores return nothing)"
        )
    if "sum(" not in query:
        sys.exit("FAIL: query should sum() so several replicas count as one queue")


def check_stability(doc: dict) -> None:
    spec = doc.get("spec") or {}
    cooldown = int(spec.get("cooldownPeriod") or 0)
    polling = int(spec.get("pollingInterval") or 0)
    if cooldown < 60:
        sys.exit(f"FAIL: cooldownPeriod={cooldown}s is too short (flaps 1<->0)")
    if polling < 10:
        sys.exit(f"FAIL: pollingInterval={polling}s is too aggressive")
    behavior = (
        ((spec.get("advanced") or {}).get("horizontalPodAutoscalerConfig") or {}).get("behavior")
        or {}
    )
    scale_down = (behavior.get("scaleDown") or {}).get("stabilizationWindowSeconds")
    if scale_down is None or int(scale_down) < 60:
        sys.exit(
            f"FAIL: scaleDown.stabilizationWindowSeconds={scale_down}; "
            "without a window, HPA drops replicas the moment the queue is empty"
        )
    meta = ((spec.get("triggers") or [{}])[0].get("metadata") or {})
    threshold = float(meta.get("threshold") or 0)
    if threshold < 1:
        sys.exit(f"FAIL: threshold={threshold} treats noise as load")


CHECKS = {
    "servicemonitor": check_servicemonitor,
    "query": check_query,
    "stability": check_stability,
}

if __name__ == "__main__":
    doc = load(sys.argv[1])
    CHECKS[sys.argv[2]](doc)
    print("OK")
