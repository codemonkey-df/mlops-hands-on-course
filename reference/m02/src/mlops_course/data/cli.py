"""Command line entry point for data generation.

Examples:
    uv run python -m mlops_course.data.cli --out data/raw
    uv run python -m mlops_course.data.cli --out s3://datasets/churn --drift 0.5
    uv run python -m mlops_course.data.cli --params params.yaml --out data/raw
"""

import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

import yaml

from mlops_course.data.churn import generate_customers
from mlops_course.data.config import GeneratorConfig, S3Settings
from mlops_course.data.storage import write_partitioned
from mlops_course.data.tickets import generate_tickets

logger = logging.getLogger(__name__)


def _load_params(path: Path | None) -> dict[str, object]:
    """Read the `generate:` section of a DVC params file (or nothing)."""
    if path is None:
        return {}
    with path.open() as fh:
        params: dict[str, object] = yaml.safe_load(fh).get("generate", {})
    return params


def main(argv: list[str] | None = None) -> None:
    """Generate N daily snapshots of churn data plus a ticket file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="local dir or s3://bucket/prefix")
    parser.add_argument("--params", type=Path, help="params.yaml with a `generate:` section")
    parser.add_argument("--days", type=int, default=None, help="number of daily snapshots")
    parser.add_argument("--drift", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--start", type=date.fromisoformat, default=None)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # Precedence: CLI flag > params.yaml > defaults
    params = _load_params(args.params)
    for key in ("days", "drift", "seed", "start"):
        if getattr(args, key) is not None:
            params[key] = getattr(args, key)
    days = int(params.pop("days", 3))  # type: ignore[call-overload]
    start = params.pop("start", date(2026, 10, 1))
    if isinstance(start, str):
        start = date.fromisoformat(start)

    s3 = S3Settings()
    for offset in range(days):
        # Each day gets its own seed so snapshots differ, but stay reproducible.
        cfg = GeneratorConfig.model_validate(
            {**params, "snapshot_date": start + timedelta(days=offset)}  # type: ignore[operator]
        )
        cfg = cfg.model_copy(update={"seed": cfg.seed + offset})
        write_partitioned(generate_customers(cfg), f"{args.out}/churn", s3, "snapshot_date")

    tickets = generate_tickets(GeneratorConfig.model_validate(params))
    if args.out.startswith("s3://"):
        tickets.write_parquet(f"{args.out}/tickets.parquet", storage_options=s3.polars_options())
    else:
        Path(args.out).mkdir(parents=True, exist_ok=True)
        tickets.write_parquet(f"{args.out}/tickets.parquet")
    logger.info("done: %d snapshots + %d tickets in %s", days, tickets.height, args.out)


if __name__ == "__main__":
    main()
