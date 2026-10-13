"""Train a churn model and track everything in MLflow.

Examples:
    export MLFLOW_TRACKING_URI=http://mlflow.YOUR_SERVER_IP.nip.io:8080
    uv run python -m mlops_course.training.train --model logreg
    uv run python -m mlops_course.training.train --model mlp --epochs 30 --lr 0.003
"""

import argparse
import json
import logging
import pickle
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import mlflow
import numpy as np
import pandas as pd
import polars as pl
import torch
from mlflow.models import infer_signature
from pydantic import BaseModel, Field
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from torch import nn

from mlops_course.data.config import S3Settings
from mlops_course.training.features import LABEL, Standardizer, to_matrix
from mlops_course.training.model import ChurnMLP, ChurnPyfunc

logger = logging.getLogger(__name__)

RAW_INPUT_COLUMNS = [
    "plan",
    "region",
    "tenure_months",
    "monthly_spend",
    "support_tickets_90d",
    "days_since_last_order",
    "app_sessions_30d",
    "discount_used",
]


class TrainConfig(BaseModel):
    """Hyper-parameters. Every field is logged as an MLflow param."""

    model: Literal["mlp", "logreg"] = "mlp"
    epochs: int = Field(default=20, gt=0)
    lr: float = Field(default=3e-3, gt=0)
    hidden: int = 32
    batch_size: int = 256
    val_fraction: float = Field(default=0.2, gt=0, lt=1)
    seed: int = 0
    experiment: str = "churn"
    data_version: str = "unknown"  # e.g. the dvc.lock md5 or a Dagster partition


@dataclass
class TrainResult:
    """What callers (CLI, Dagster in M4) need back."""

    run_id: str
    model_uri: str
    metrics: dict[str, float]


def _split(df: pl.DataFrame, cfg: TrainConfig) -> tuple[pl.DataFrame, pl.DataFrame]:
    shuffled = df.sample(fraction=1.0, shuffle=True, seed=cfg.seed)
    n_val = int(df.height * cfg.val_fraction)
    return shuffled.slice(n_val), shuffled.slice(0, n_val)


def _fit_mlp(
    x: np.ndarray, y: np.ndarray, xv: np.ndarray, yv: np.ndarray, cfg: TrainConfig
) -> ChurnMLP:
    torch.manual_seed(cfg.seed)
    model = ChurnMLP(n_features=x.shape[1], hidden=cfg.hidden)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    # Class imbalance (~13% churn): weight positives so the model doesn't
    # learn "nobody churns" and still get 87% accuracy.
    pos_weight = torch.tensor((1 - y.mean()) / max(y.mean(), 1e-6))
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    xt, yt = torch.from_numpy(x), torch.from_numpy(y.astype(np.float32))
    for epoch in range(cfg.epochs):
        model.train()
        perm = torch.randperm(len(xt))
        total = 0.0
        for i in range(0, len(xt), cfg.batch_size):
            idx = perm[i : i + cfg.batch_size]
            opt.zero_grad()
            loss = loss_fn(model(xt[idx]), yt[idx])
            loss.backward()
            opt.step()
            total += loss.item() * len(idx)
        model.eval()
        with torch.no_grad():
            val_proba = torch.sigmoid(model(torch.from_numpy(xv))).numpy()
        # step=epoch -> MLflow draws a curve instead of overwriting one value.
        mlflow.log_metrics(
            {"train_loss": total / len(xt), "val_auc_epoch": roc_auc_score(yv, val_proba)},
            step=epoch,
        )
    return model


def _data_version() -> str:
    """Best-effort lineage: md5 of data/raw from dvc.lock, else 'unknown'."""
    lock = Path("dvc.lock")
    if not lock.exists():
        return "unknown"
    import yaml

    outs = yaml.safe_load(lock.read_text())["stages"]["generate"]["outs"]
    return str(outs[0]["md5"])


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def train(df: pl.DataFrame, cfg: TrainConfig) -> TrainResult:
    """Train, evaluate and log one model as an MLflow run.

    Args:
        df: Raw customer rows (CHURN_SCHEMA), label included.
        cfg: Hyper-parameters.

    Returns:
        Run id, model URI and the validation metrics.
    """
    mlflow.set_experiment(cfg.experiment)  # created on first use
    train_df, val_df = _split(df, cfg)
    x_raw, xv_raw = to_matrix(train_df), to_matrix(val_df)
    y, yv = train_df[LABEL].to_numpy(), val_df[LABEL].to_numpy()
    scaler = Standardizer.fit(x_raw)  # fitted on TRAIN only
    x, xv = scaler.transform(x_raw), scaler.transform(xv_raw)

    with mlflow.start_run(run_name=f"{cfg.model}-e{cfg.epochs}") as run:
        mlflow.log_params(cfg.model_dump())
        mlflow.set_tags({"git_commit": _git_commit(), "rows": df.height})

        with tempfile.TemporaryDirectory() as tmp:
            scaler_path = Path(tmp) / "scaler.json"
            scaler_path.write_text(json.dumps(scaler.to_dict()))
            if cfg.model == "mlp":
                net = _fit_mlp(x, y, xv, yv, cfg)
                with torch.no_grad():
                    val_proba = torch.sigmoid(net(torch.from_numpy(xv))).numpy()
                weights = Path(tmp) / "weights.pt"
                torch.save(net.state_dict(), weights)
            else:
                clf = LogisticRegression(max_iter=1000, class_weight="balanced").fit(x, y)
                val_proba = clf.predict_proba(xv)[:, 1]
                weights = Path(tmp) / "weights.pkl"
                weights.write_bytes(pickle.dumps(clf))

            metrics = {
                "val_auc": float(roc_auc_score(yv, val_proba)),
                "val_f1": float(f1_score(yv, val_proba > 0.5)),
                "val_churn_rate": float(yv.mean()),
            }
            mlflow.log_metrics(metrics)

            example = val_df.select(RAW_INPUT_COLUMNS).head(5).to_pandas()
            model_info = mlflow.pyfunc.log_model(
                name="model",
                python_model=ChurnPyfunc(),
                artifacts={"weights": str(weights), "scaler": str(scaler_path)},
                model_config={"kind": cfg.model, "hidden": cfg.hidden},
                # The signature = the input/output contract. MLflow validates
                # requests against it when serving.
                signature=infer_signature(example, _example_output(len(example))),
                input_example=example,
                pip_requirements=["torch", "scikit-learn", "polars", "pandas", "numpy"],
                code_paths=[str(Path(__file__).resolve().parents[1])],  # ship mlops_course
            )
    logger.info("run %s: %s", run.info.run_id, metrics)
    return TrainResult(run.info.run_id, model_info.model_uri, metrics)


def _example_output(n: int) -> pd.DataFrame:
    """Shape of the model output, used to infer the signature."""
    return pd.DataFrame({"churn_probability": [0.5] * n})


def load_training_data(s3: S3Settings, uri: str = "s3://datasets/churn") -> pl.DataFrame:
    """Read all snapshots from the lake (Hive partitions -> snapshot_date column)."""
    return pl.scan_parquet(
        f"{uri}/**/*.parquet", hive_partitioning=True, storage_options=s3.polars_options()
    ).collect()


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["mlp", "logreg"], default="mlp")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--hidden", type=int, default=32)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    df = load_training_data(S3Settings())
    cfg = TrainConfig(
        model=args.model,
        epochs=args.epochs,
        lr=args.lr,
        hidden=args.hidden,
        data_version=_data_version(),
    )
    result = train(df, cfg)
    logger.info(
        json.dumps({"run_id": result.run_id, "model_uri": result.model_uri, **result.metrics})
    )


if __name__ == "__main__":
    main()
