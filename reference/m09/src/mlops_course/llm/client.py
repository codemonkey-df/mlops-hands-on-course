"""Answer support tickets through the LiteLLM router with the plain OpenAI SDK.

The application only knows ONE endpoint and model GROUP names; which pod,
fallback or retry serves the request is the router's business.

    uv run python -m mlops_course.llm.client --n 20 --concurrency 4
"""

import argparse
import asyncio
import logging
import time
from collections import Counter
from collections.abc import Iterable, Mapping

from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from mlops_course.data.config import GeneratorConfig
from mlops_course.data.tickets import generate_tickets

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a concise customer-support assistant."


class LLMSettings(BaseSettings):
    """Router endpoint + key from env (LLM_BASE_URL, LLM_API_KEY) or `.env`."""

    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    base_url: str = "http://llm.YOUR_SERVER_IP.nip.io:8080/v1"  # note the /v1
    api_key: str = ""


class TicketAnswer(BaseModel):
    """One answered ticket."""

    ticket_id: str
    requested_model: str
    served_model: str  # differs from requested_model when the router fell back
    text: str
    latency_s: float


class TicketAnswerer:
    """Send tickets to the model named by their `route`, with bounded concurrency."""

    def __init__(self, client: AsyncOpenAI, concurrency: int = 4, max_tokens: int = 64) -> None:
        self._client = client
        self._slots = asyncio.Semaphore(concurrency)
        self._max_tokens = max_tokens

    async def answer(self, ticket: Mapping[str, str]) -> TicketAnswer:
        """Answer one ticket (dict with ticket_id, route, text)."""
        async with self._slots:
            start = time.perf_counter()
            resp = await self._client.chat.completions.create(
                model=ticket["route"],
                max_tokens=self._max_tokens,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": ticket["text"]},
                ],
            )
            return TicketAnswer(
                ticket_id=ticket["ticket_id"],
                requested_model=ticket["route"],
                served_model=resp.model,
                text=resp.choices[0].message.content or "",
                latency_s=time.perf_counter() - start,
            )

    async def answer_all(self, tickets: Iterable[Mapping[str, str]]) -> list[TicketAnswer]:
        """Answer all tickets concurrently (order preserved)."""
        return list(await asyncio.gather(*(self.answer(t) for t in tickets)))


async def _run(n: int, concurrency: int, drift: float) -> None:
    settings = LLMSettings()
    tickets = generate_tickets(GeneratorConfig(drift=drift), n=n).to_dicts()
    # max_retries=0: the ROUTER retries; retrying here too multiplies the load.
    async with AsyncOpenAI(
        base_url=settings.base_url, api_key=settings.api_key, max_retries=0, timeout=180
    ) as client:
        start = time.perf_counter()
        answers = await TicketAnswerer(client, concurrency).answer_all(tickets)
    elapsed = time.perf_counter() - start
    for a in answers[:3]:
        logger.info("%s %s -> %s: %s", a.ticket_id, a.requested_model, a.served_model, a.text[:60])
    logger.info("served by: %s", dict(Counter(a.served_model for a in answers)))
    fallbacks = sum(a.served_model != a.requested_model for a in answers)
    logger.info("%d tickets in %.1fs, %d fell back", len(answers), elapsed, fallbacks)


def main() -> None:
    """CLI: answer N synthetic tickets."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    for transport in ("httpx", "httpx2"):  # openai>=3 ships its own httpx2 fork
        logging.getLogger(transport).setLevel(logging.WARNING)
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--drift", type=float, default=0.0, help="more complex tickets (0..1)")
    args = p.parse_args()
    asyncio.run(_run(args.n, args.concurrency, args.drift))


if __name__ == "__main__":
    main()
