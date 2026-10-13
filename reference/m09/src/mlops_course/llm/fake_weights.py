"""Create fake "model weights" and upload them to MinIO (s3://llm-weights/<model>/).

The layout mimics a Hugging Face snapshot, which is what `vllm serve <dir>`
loads. In real life you would `huggingface-cli download` ONCE on a machine with
internet and mirror the folder into MinIO; the cluster never talks to the Hub.

    uv run python -m mlops_course.llm.fake_weights small-chat --size-mb 50 --max-len 4096
"""

import argparse
import json
import logging
import os
import tempfile
from pathlib import Path

from pyarrow import fs

from mlops_course.data.config import S3Settings

logger = logging.getLogger(__name__)


def make_fake_weights(out: Path, size_mb: int, max_position_embeddings: int) -> Path:
    """Write config.json, tokenizer files and a random `model.safetensors` of `size_mb`."""
    out.mkdir(parents=True, exist_ok=True)
    config = {
        "architectures": ["MockForCausalLM"],
        "model_type": "mock",
        "max_position_embeddings": max_position_embeddings,
        "torch_dtype": "bfloat16",
    }
    (out / "config.json").write_text(json.dumps(config, indent=2))
    (out / "tokenizer_config.json").write_text(
        json.dumps({"model_max_length": max_position_embeddings})
    )
    with (out / "model.safetensors").open("wb") as f:
        for _ in range(size_mb):
            f.write(os.urandom(1024 * 1024))  # chunked: never hold the whole file in RAM
    return out


def upload(local: Path, bucket: str, prefix: str, s3: S3Settings) -> None:
    """Copy a local folder to s3://bucket/prefix/ with pyarrow's S3 filesystem."""
    scheme, host = s3.endpoint_url.split("://", 1)
    remote = fs.S3FileSystem(
        access_key=s3.access_key,
        secret_key=s3.secret_key,
        endpoint_override=host,
        scheme=scheme,
        region=s3.region,
    )
    fs.copy_files(str(local), f"{bucket}/{prefix}", destination_filesystem=remote)
    logger.info("uploaded %s -> s3://%s/%s", local, bucket, prefix)


def main() -> None:
    """CLI: generate fake weights for one model and upload them."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--size-mb", type=int, default=50)
    p.add_argument("--max-len", type=int, default=4096)
    p.add_argument("--bucket", default="llm-weights")
    args = p.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        local = make_fake_weights(Path(tmp) / args.model, args.size_mb, args.max_len)
        upload(local, args.bucket, args.model, S3Settings())


if __name__ == "__main__":
    main()
