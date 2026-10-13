"""Model registry workflow with aliases (champion / challenger).

MLflow 2.9+ deprecated "stages" (Staging/Production). Aliases replace them:
an alias is a movable pointer to ONE version, e.g.
    models:/churn-classifier@champion  -> version 3
Serving loads `@champion`; promotion = moving the alias. Rollback = moving it back.

Examples:
    uv run python -m mlops_course.training.registry register --run-id <id>
    uv run python -m mlops_course.training.registry promote
    uv run python -m mlops_course.training.registry show
"""

import argparse
import logging
from dataclasses import dataclass

import mlflow
import polars as pl
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from sklearn.metrics import roc_auc_score

from mlops_course.data.config import S3Settings
from mlops_course.training.features import LABEL
from mlops_course.training.train import load_training_data

logger = logging.getLogger(__name__)

MODEL_NAME = "churn-classifier"
CHAMPION, CHALLENGER = "champion", "challenger"


@dataclass
class PromotionDecision:
    """Outcome of a champion/challenger comparison."""

    promoted: bool
    challenger_version: str
    champion_version: str | None
    challenger_auc: float
    champion_auc: float | None


def register(run_id: str, client: MlflowClient | None = None) -> str:
    """Register the run's model as a new version and point `@challenger` at it.

    Args:
        run_id: MLflow run that logged a model under the name "model".
        client: Injected for tests; defaults to a client on the tracking URI.

    Returns:
        The new version number (as string).
    """
    client = client or MlflowClient()
    # Model URI by run: the logged model named "model" inside that run.
    version = mlflow.register_model(f"runs:/{run_id}/model", MODEL_NAME)
    client.set_registered_model_alias(MODEL_NAME, CHALLENGER, version.version)
    logger.info("registered %s v%s as @%s", MODEL_NAME, version.version, CHALLENGER)
    return str(version.version)


def _auc(alias: str, holdout: pl.DataFrame) -> tuple[str, float] | None:
    client = MlflowClient()
    try:
        mv = client.get_model_version_by_alias(MODEL_NAME, alias)
    except MlflowException:
        return None  # alias doesn't exist yet (first ever model)
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}@{alias}")
    proba = model.predict(holdout.to_pandas())["churn_probability"]
    return str(mv.version), float(roc_auc_score(holdout[LABEL].to_numpy(), proba))


def promote(holdout: pl.DataFrame, min_gain: float = 0.0) -> PromotionDecision:
    """Move `@champion` to `@challenger` if it is better on the holdout set.

    Both models are scored on the SAME fresh data: comparing their logged
    validation metrics would compare numbers from different datasets.

    Args:
        holdout: Labelled rows neither model was trained on (e.g. newest snapshot).
        min_gain: Required AUC improvement, guards against noise-driven flips.
    """
    challenger = _auc(CHALLENGER, holdout)
    if challenger is None:
        raise RuntimeError(f"no @{CHALLENGER} for {MODEL_NAME}: register a model first")
    champion = _auc(CHAMPION, holdout)
    better = champion is None or challenger[1] >= champion[1] + min_gain
    if better:
        MlflowClient().set_registered_model_alias(MODEL_NAME, CHAMPION, challenger[0])
    decision = PromotionDecision(
        promoted=better,
        challenger_version=challenger[0],
        champion_version=champion[0] if champion else None,
        challenger_auc=challenger[1],
        champion_auc=champion[1] if champion else None,
    )
    logger.info("promotion decision: %s", decision)
    return decision


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    reg = sub.add_parser("register")
    reg.add_argument("--run-id", required=True)
    pro = sub.add_parser("promote")
    pro.add_argument("--min-gain", type=float, default=0.0)
    sub.add_parser("show")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    if args.cmd == "register":
        register(args.run_id)
    elif args.cmd == "promote":
        data = load_training_data(S3Settings())
        newest = data["snapshot_date"].max()
        promote(data.filter(pl.col("snapshot_date") == newest), args.min_gain)
    else:
        model = MlflowClient().get_registered_model(MODEL_NAME)
        logger.info("%s aliases: %s", MODEL_NAME, model.aliases)


if __name__ == "__main__":
    main()
