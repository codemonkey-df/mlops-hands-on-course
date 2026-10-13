"""Copy a registered MLflow model into the local BentoML model store.

Resolves an alias (``@champion``) to a concrete version ONCE, at build time,
so the resulting Bento/image always serves exactly that version.

Usage:
    uv run python -m mlops_course.serving.import_model --alias champion
"""

import argparse
import logging

import bentoml
from mlflow import MlflowClient

from mlops_course.training.registry import MODEL_NAME

logger = logging.getLogger(__name__)

BENTO_MODEL_NAME = "churn-classifier"


def import_from_registry(alias: str = "champion", client: MlflowClient | None = None) -> str:
    """Import ``models:/<MODEL_NAME>@<alias>`` into the BentoML store.

    Args:
        alias: Registry alias to resolve.
        client: MLflow client (injected in tests); defaults to the env config.

    Returns:
        The BentoML model tag, e.g. ``churn-classifier:mv7``.
    """
    client = client or MlflowClient()
    mv = client.get_model_version_by_alias(MODEL_NAME, alias)
    tag = f"{BENTO_MODEL_NAME}:mv{mv.version}"
    try:
        existing = bentoml.models.get(tag)
        logger.info("%s already in the store, skipping import", existing.tag)
        return str(existing.tag)
    except bentoml.exceptions.NotFound:
        pass
    model = bentoml.mlflow.import_model(
        tag,
        model_uri=f"models:/{MODEL_NAME}/{mv.version}",  # the version, NOT the alias
        labels={"mlflow_version": str(mv.version), "alias": alias},
        metadata={"run_id": mv.run_id or "", "source": mv.source or ""},
    )
    logger.info("imported %s from %s v%s", model.tag, MODEL_NAME, mv.version)
    return str(model.tag)


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alias", default="champion")
    args = parser.parse_args()
    import_from_registry(args.alias)


if __name__ == "__main__":
    main()
