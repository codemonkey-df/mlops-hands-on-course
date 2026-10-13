"""The ticket client routes each ticket to the model its intent needs."""

import asyncio
from pathlib import Path

import httpx
import pytest
from openai import AsyncOpenAI

from mlops_course.llm.client import TicketAnswerer
from mlops_course.llm.mock_vllm import MockSettings, create_app


@pytest.fixture
def openai_client(tmp_path: Path) -> AsyncOpenAI:
    # The mock app stands in for the router: same API, in-process, no network.
    app = create_app(
        MockSettings(
            model_path=tmp_path,
            served_model_names=["small-chat", "big-reasoning"],
            load_seconds=0,
            ttft_seconds=0,
            tokens_per_second=10_000,
        )
    )
    http = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
    return AsyncOpenAI(base_url="http://test/v1", api_key="sk-test", http_client=http)


@pytest.fixture
def tickets() -> list[dict[str, str]]:
    return [
        {"ticket_id": "T1", "intent": "billing", "route": "small-chat", "text": "invoice?"},
        {"ticket_id": "T2", "intent": "technical", "route": "big-reasoning", "text": "crash"},
    ]


def test_each_ticket_goes_to_its_route(
    openai_client: AsyncOpenAI, tickets: list[dict[str, str]]
) -> None:
    answers = asyncio.run(TicketAnswerer(openai_client, concurrency=2).answer_all(tickets))
    assert [a.served_model for a in answers] == ["small-chat", "big-reasoning"]
    assert all(a.text.startswith(f"[{a.served_model}]") for a in answers)
    assert all(a.latency_s >= 0 for a in answers)
