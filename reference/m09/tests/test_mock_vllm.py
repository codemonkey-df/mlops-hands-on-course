"""Tests for the vLLM-compatible mock server (in-process, no network)."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mlops_course.llm.mock_vllm import MockSettings, WeightsMissingError, create_app, parse_args


@pytest.fixture
def weights(tmp_path: Path) -> Path:
    (tmp_path / "config.json").write_text('{"architectures": ["MockForCausalLM"]}')
    return tmp_path


@pytest.fixture
def settings(weights: Path) -> MockSettings:
    return MockSettings(
        model_path=weights,
        served_model_names=["small-chat"],
        max_model_len=256,
        max_num_seqs=2,
        load_seconds=0,
        ttft_seconds=0,
        tokens_per_second=10_000,
    )


@pytest.fixture
def client(settings: MockSettings) -> TestClient:
    with TestClient(create_app(settings)) as c:
        yield c


def chat(model: str = "small-chat", **extra: object) -> dict[str, object]:
    return {
        "model": model,
        "messages": [{"role": "user", "content": "How do I reset my password?"}],
        **extra,
    }


def test_parse_args_accepts_real_vllm_flags(weights: Path) -> None:
    s = parse_args(
        [
            "serve",
            str(weights),
            "--served-model-name",
            "small-chat",
            "--max-model-len",
            "4096",
            "--gpu-memory-utilization",
            "0.9",
            "--tensor-parallel-size",
            "1",
            "--dtype",
            "auto",
        ]
    )
    assert s.served_model_names == ["small-chat"]
    assert s.max_model_len == 4096


def test_missing_weights_refuse_to_start(tmp_path: Path) -> None:
    s = MockSettings(model_path=tmp_path / "nope", served_model_names=["x"], load_seconds=0)
    with pytest.raises(WeightsMissingError), TestClient(create_app(s)):
        pass


def test_models_lists_served_names(client: TestClient) -> None:
    ids = [m["id"] for m in client.get("/v1/models").json()["data"]]
    assert ids == ["small-chat"]


def test_chat_completion_shape_and_usage(client: TestClient) -> None:
    body = client.post("/v1/chat/completions", json=chat(max_tokens=16)).json()
    assert body["object"] == "chat.completion"
    assert body["model"] == "small-chat"
    assert body["choices"][0]["message"]["content"]
    assert body["usage"]["completion_tokens"] <= 16


def test_unknown_model_is_404_like_vllm(client: TestClient) -> None:
    r = client.post("/v1/chat/completions", json=chat(model="gpt-4"))
    assert r.status_code == 404
    assert "does not exist" in r.json()["message"]


def test_context_length_is_enforced(client: TestClient) -> None:
    r = client.post("/v1/chat/completions", json=chat(max_tokens=10_000))
    assert r.status_code == 400
    assert "maximum context length" in r.json()["message"]


def test_streaming_sends_chunks_then_done(client: TestClient) -> None:
    with client.stream("POST", "/v1/chat/completions", json=chat(stream=True, max_tokens=8)) as r:
        lines = [ln for ln in r.iter_lines() if ln.startswith("data: ")]
    assert lines[-1] == "data: [DONE]"
    first = json.loads(lines[0][len("data: ") :])
    assert first["object"] == "chat.completion.chunk"


def test_metrics_use_vllm_names(client: TestClient) -> None:
    client.post("/v1/chat/completions", json=chat(max_tokens=4))
    text = client.get("/metrics").text
    for name in (
        "vllm:num_requests_running",
        "vllm:num_requests_waiting",
        "vllm:time_to_first_token_seconds_bucket",
        "vllm:generation_tokens_total",
    ):
        assert name in text
    assert 'model_name="small-chat"' in text
