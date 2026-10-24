"""Static guards for V2-010 critical learner blockers (CORS, MinIO kill, docs)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MLFLOW_DEPLOYMENTS = (
    ROOT / "platform/k8s/mlflow/20-deployment.yaml",
    ROOT / "reference/m03/platform/k8s/mlflow/20-deployment.yaml",
)

CORS_FLAG = "--cors-allowed-origins=http://mlflow.YOUR_SERVER_IP.nip.io:8080"
M01_DOCS = ROOT / "docs/modules/m01-kubernetes-helm.md"
TROUBLESHOOTING = ROOT / "docs/cheatsheets/troubleshooting.md"


def test_mlflow_deployments_include_cors_with_ip_placeholder() -> None:
    """Platform + reference MLflow must list CORS so configure-ip can substitute."""
    for path in MLFLOW_DEPLOYMENTS:
        text = path.read_text(encoding="utf-8")
        assert CORS_FLAG in text, f"missing CORS flag in {path}"
        assert "--allowed-hosts=" in text, f"missing allowed-hosts in {path}"


def test_m01_docs_do_not_teach_minio_kill_1() -> None:
    """Chainguard/distroless MinIO has no kill binary; demo must use delete/rollout."""
    text = M01_DOCS.read_text(encoding="utf-8")
    assert "exec deploy/minio -- kill" not in text
    assert "kubectl -n storage exec deploy/minio -- kill" not in text
    has_rollout = "rollout restart deploy/minio" in text
    has_delete = "delete pod -l app.kubernetes.io/name=minio" in text
    assert has_rollout or has_delete


def test_troubleshooting_covers_c1_through_c5() -> None:
    """Cheatsheet must name each critical empty-UI / CORS failure mode."""
    text = TROUBLESHOOTING.read_text(encoding="utf-8")
    assert "INTERNAL_ERROR" in text or "cors-allowed" in text.lower() or "CORS" in text
    assert "Overview" in text and "Runs" in text
    assert "mlruns" in text or "MLFLOW_TRACKING_URI" in text
    assert "DAGSTER_HOME" in text
    assert "kill" in text.lower() or "EndpointSlice" in text or "endpointslices" in text
