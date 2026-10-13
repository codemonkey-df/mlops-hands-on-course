"""A tiny stand-in for `vllm serve`: same CLI flags, same OpenAI API, same metric names.

No GPU, no model: answers are canned text, "tokens" are words, latency is
simulated. Everything AROUND the model (weights download, probes, router,
metrics, autoscaling) behaves like the real thing, which is what the course is about.

    python -m mlops_course.llm.mock_vllm serve /models/small-chat \\
        --served-model-name small-chat --max-model-len 4096 --max-num-seqs 8

Mock-only knobs (env): MOCK_LOAD_SECONDS, MOCK_TTFT_SECONDS, MOCK_TOKENS_PER_SECOND.
"""

import argparse
import asyncio
import json
import logging
import os
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

CANNED = {
    "password": "To reset your password open Settings, choose Security, then Reset password "
    "and follow the link we e-mail you within a few minutes.",
    "invoice": "Invoices are in Billing, then History. Each one can be downloaded as PDF.",
    "refund": "Refunds are reviewed within five business days. Reply with your order id "
    "and we will check the status for you.",
}
DEFAULT_ANSWER = (
    "Thanks for reaching out. Let me think this through step by step: first we check "
    "your account settings, then the recent orders, and finally the open tickets."
)


class WeightsMissingError(RuntimeError):
    """Raised at startup when the model directory has no config.json (like vLLM)."""


class MockSettings(BaseModel):
    """The subset of vLLM settings the mock honours, plus simulation knobs."""

    model_path: Path
    served_model_names: list[str]
    max_model_len: int = 4096
    max_num_seqs: int = 8  # concurrent sequences; extra requests WAIT
    host: str = "0.0.0.0"
    port: int = 8000
    load_seconds: float = Field(default_factory=lambda: float(os.getenv("MOCK_LOAD_SECONDS", "5")))
    ttft_seconds: float = Field(
        default_factory=lambda: float(os.getenv("MOCK_TTFT_SECONDS", "0.15"))
    )
    tokens_per_second: float = Field(
        default_factory=lambda: float(os.getenv("MOCK_TOKENS_PER_SECOND", "40"))
    )


def parse_args(argv: list[str] | None = None) -> MockSettings:
    """Parse `vllm serve`-style arguments; unknown vLLM flags are accepted and logged."""
    p = argparse.ArgumentParser(prog="mock-vllm")
    p.add_argument("command", choices=["serve"])
    p.add_argument("model")
    p.add_argument("--served-model-name", nargs="+")
    p.add_argument("--max-model-len", type=int, default=4096)
    p.add_argument("--max-num-seqs", type=int, default=8)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8000)
    args, unknown = p.parse_known_args(argv)
    if unknown:
        logger.info("accepted (and ignored) vLLM flags: %s", " ".join(unknown))
    return MockSettings(
        model_path=Path(args.model),
        served_model_names=args.served_model_name or [args.model],
        max_model_len=args.max_model_len,
        max_num_seqs=args.max_num_seqs,
        host=args.host,
        port=args.port,
    )


class Metrics:
    """vLLM metric names, so dashboards and KEDA queries work unchanged on real vLLM."""

    def __init__(self, model_name: str) -> None:
        self.registry = CollectorRegistry()
        r, lbl = self.registry, ["model_name"]
        self.running = Gauge("vllm:num_requests_running", "Requests running", lbl, registry=r)
        self.waiting = Gauge("vllm:num_requests_waiting", "Requests waiting", lbl, registry=r)
        self.kv_cache = Gauge("vllm:kv_cache_usage_perc", "KV-cache usage (0-1)", lbl, registry=r)
        buckets = [0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30]
        self.ttft = Histogram(
            "vllm:time_to_first_token_seconds", "TTFT", lbl, buckets=buckets, registry=r
        )
        self.e2e = Histogram(
            "vllm:e2e_request_latency_seconds", "E2E latency", lbl, buckets=buckets, registry=r
        )
        self.prompt_tokens = Counter("vllm:prompt_tokens", "Prompt tokens", lbl, registry=r)
        self.gen_tokens = Counter("vllm:generation_tokens", "Generated tokens", lbl, registry=r)
        self.success = Counter(
            "vllm:request_success", "Finished requests", [*lbl, "finished_reason"], registry=r
        )
        self.model = model_name
        for g in (self.running, self.waiting, self.kv_cache):
            g.labels(model_name).set(0)


class Engine:
    """Simulated engine: at most `max_num_seqs` requests run, the rest queue."""

    def __init__(self, settings: MockSettings, metrics: Metrics) -> None:
        self.s = settings
        self.m = metrics
        self._slots = asyncio.Semaphore(settings.max_num_seqs)
        self._running = 0
        self._waiting = 0

    def _publish(self) -> None:
        name = self.m.model
        self.m.running.labels(name).set(self._running)
        self.m.waiting.labels(name).set(self._waiting)
        self.m.kv_cache.labels(name).set(self._running / self.s.max_num_seqs)

    async def generate(self, prompt: str, max_tokens: int, model: str) -> AsyncIterator[str]:
        """Yield answer "tokens" (words) with simulated TTFT and decode speed."""
        start = time.perf_counter()
        self._waiting += 1
        self._publish()
        async with self._slots:
            self._waiting -= 1
            self._running += 1
            self._publish()
            try:
                answer = next((v for k, v in CANNED.items() if k in prompt.lower()), DEFAULT_ANSWER)
                words = f"[{model}] {answer}".split()[:max_tokens]
                await asyncio.sleep(self.s.ttft_seconds)
                self.m.ttft.labels(self.m.model).observe(time.perf_counter() - start)
                for i, w in enumerate(words):
                    if i:
                        await asyncio.sleep(1 / self.s.tokens_per_second)
                    self.m.gen_tokens.labels(self.m.model).inc()
                    yield w if i == 0 else " " + w
                reason = "length" if len(words) == max_tokens else "stop"
                self.m.success.labels(self.m.model, reason).inc()
            finally:
                self._running -= 1
                self._publish()
                self.m.e2e.labels(self.m.model).observe(time.perf_counter() - start)


def _error(status: int, message: str, err_type: str) -> JSONResponse:
    # vLLM's error body (flat, not OpenAI's {"error": {...}} wrapper).
    body = {"object": "error", "message": message, "type": err_type, "param": None, "code": status}
    return JSONResponse(body, status_code=status)


def _count_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def create_app(settings: MockSettings) -> FastAPI:
    """Build the FastAPI app (dependency-injected settings; no globals)."""
    metrics = Metrics(settings.served_model_names[0])
    engine = Engine(settings, metrics)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # Real vLLM loads weights BEFORE the HTTP server accepts connections:
        # probes get "connection refused" until this finishes.
        if not (settings.model_path / "config.json").is_file():
            raise WeightsMissingError(f"no config.json in {settings.model_path}")
        logger.info("loading %s (simulated %.0fs)", settings.model_path, settings.load_seconds)
        await asyncio.sleep(settings.load_seconds)
        logger.info("serving %s", settings.served_model_names)
        yield

    app = FastAPI(title="mock-vllm", lifespan=lifespan)

    @app.get("/health")
    async def health() -> PlainTextResponse:
        return PlainTextResponse("")

    @app.get("/metrics")
    async def prom() -> PlainTextResponse:
        return PlainTextResponse(generate_latest(metrics.registry).decode())

    @app.get("/v1/models")
    async def models() -> dict[str, Any]:
        data = [
            {
                "id": n,
                "object": "model",
                "owned_by": "vllm",
                "max_model_len": settings.max_model_len,
            }
            for n in settings.served_model_names
        ]
        return {"object": "list", "data": data}

    @app.post("/v1/chat/completions", response_model=None)
    async def chat(request: Request) -> JSONResponse | StreamingResponse:
        req = await request.json()
        model = req.get("model")
        if model not in settings.served_model_names:
            return _error(404, f"The model `{model}` does not exist.", "NotFoundError")
        prompt = " ".join(str(m.get("content", "")) for m in req.get("messages", []))
        prompt_tokens = _count_tokens(prompt)
        max_tokens = int(req.get("max_tokens") or req.get("max_completion_tokens") or 64)
        if prompt_tokens + max_tokens > settings.max_model_len:
            return _error(
                400,
                f"This model's maximum context length is {settings.max_model_len} tokens. "
                f"However, you requested {prompt_tokens + max_tokens} tokens.",
                "BadRequestError",
            )
        metrics.prompt_tokens.labels(metrics.model).inc(prompt_tokens)
        rid, created = f"chatcmpl-{uuid.uuid4().hex}", int(time.time())

        if req.get("stream"):

            async def sse() -> AsyncIterator[str]:
                def chunk(delta: dict[str, str], finish: str | None = None) -> str:
                    c = {
                        "id": rid,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
                    }
                    return f"data: {json.dumps(c)}\n\n"

                yield chunk({"role": "assistant", "content": ""})
                async for tok in engine.generate(prompt, max_tokens, model):
                    yield chunk({"content": tok})
                yield chunk({}, "stop")
                yield "data: [DONE]\n\n"

            return StreamingResponse(sse(), media_type="text/event-stream")

        tokens = [t async for t in engine.generate(prompt, max_tokens, model)]
        text = "".join(tokens)
        return JSONResponse(
            {
                "id": rid,
                "object": "chat.completion",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": text},
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": len(tokens),
                    "total_tokens": prompt_tokens + len(tokens),
                },
            }
        )

    return app


def main() -> None:
    """CLI entry point: `python -m mlops_course.llm.mock_vllm serve <model> [vLLM flags]`."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = parse_args()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port, log_level="warning")


if __name__ == "__main__":
    main()
