"""Fake model weights look like a Hugging Face snapshot (what vLLM loads)."""

import json
from pathlib import Path

from mlops_course.llm.fake_weights import make_fake_weights


def test_layout_matches_hf_snapshot(tmp_path: Path) -> None:
    out = make_fake_weights(tmp_path / "small-chat", size_mb=1, max_position_embeddings=4096)
    names = {p.name for p in out.iterdir()}
    assert {"config.json", "tokenizer_config.json", "model.safetensors"} <= names
    assert json.loads((out / "config.json").read_text())["max_position_embeddings"] == 4096
    assert (out / "model.safetensors").stat().st_size == 1024 * 1024
