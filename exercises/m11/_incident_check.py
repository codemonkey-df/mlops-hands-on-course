"""Static checks for the M11 incident files.

Usage: python _incident_check.py <path> <check-name>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


def check_psi(path: str) -> None:
    text = Path(path).read_text()
    match = re.search(r"^PSI_ALERT\s*=\s*([0-9.]+)", text, re.M)
    if not match:
        sys.exit("FAIL: PSI_ALERT assignment not found")
    value = float(match.group(1))
    if value > 0.25:
        sys.exit(
            f"FAIL: PSI_ALERT={value} will never fire "
            "(significant drift is typically 0.2–1.0)"
        )
    if value <= 0:
        sys.exit("FAIL: PSI_ALERT must be positive")


def check_ci(path: str) -> None:
    text = Path(path).read_text()
    if "platform/gitops/serving/kustomization.yaml" not in text:
        sys.exit(
            "FAIL: sed must edit platform/gitops/serving/kustomization.yaml "
            "(Argo CD watches GitOps, not the M6 hand-applied manifests)"
        )
    if "ci:churn-tag" not in text:
        sys.exit("FAIL: missing # ci:churn-tag marker the sed expression keys on")
    if re.search(r"platform/k8s/serving/churn\.yaml", text):
        sys.exit("FAIL: still writing the tag into platform/k8s/serving/churn.yaml")


def check_app(path: str) -> None:
    doc = yaml.safe_load(Path(path).read_text())
    auto = ((doc.get("spec") or {}).get("syncPolicy") or {}).get("automated")
    if not isinstance(auto, dict):
        sys.exit("FAIL: spec.syncPolicy.automated missing — Argo CD will not sync")
    if auto.get("selfHeal") is not True:
        sys.exit("FAIL: selfHeal is not true — manual kubectl edits will stick")
    if auto.get("prune") is not True:
        sys.exit("FAIL: prune is not true — deleted Git resources linger in the cluster")


def check_dashboard(path: str) -> None:
    text = Path(path).read_text()
    if "churn_prediction_probability" not in text:
        sys.exit(
            "FAIL: dashboard does not query churn_prediction_probability "
            "(that is the histogram the Bento service records)"
        )
    if "churn_score_bucket" in text:
        sys.exit("FAIL: still querying churn_score_bucket, which does not exist")


CHECKS = {
    "psi": check_psi,
    "ci": check_ci,
    "app": check_app,
    "dashboard": check_dashboard,
}

if __name__ == "__main__":
    CHECKS[sys.argv[2]](sys.argv[1])
    print("OK")
