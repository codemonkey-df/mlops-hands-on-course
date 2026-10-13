"""Synthetic support tickets: prompts for the LLM part of the course (M9).

Each ticket has an intent and a `route`: which LLM should answer it.
Simple intents go to a small fast model, complex ones to a big model.
The router in M9 learns to make exactly this decision.
"""

import numpy as np
import polars as pl

from mlops_course.data.config import GeneratorConfig

INTENTS = ["billing", "shipping", "technical", "cancellation", "chit-chat"]
ROUTES = {
    "billing": "small-chat",
    "shipping": "small-chat",
    "chit-chat": "small-chat",
    "technical": "big-reasoning",
    "cancellation": "big-reasoning",
}
_TEMPLATES = {
    "billing": [
        "I was charged twice for order {order}, can you refund one?",
        "Why is my invoice for {month} higher than usual?",
    ],
    "shipping": [
        "Where is my package {order}? Tracking hasn't updated in {days} days.",
        "Can I change the delivery address for order {order}?",
    ],
    "technical": [
        "The app crashes when I open my order history after the {month} update. "
        "I reinstalled twice and cleared the cache, still broken on Android.",
        "Checkout fails with error {code} when I use a saved card, but works with a new one.",
    ],
    "cancellation": [
        "I want to cancel my {plan} plan. Your competitor is cheaper and I had {days} "
        "days of problems. What can you offer me before I leave?",
    ],
    "chit-chat": ["Hi! Just wanted to say the new design looks great.", "Thanks for the help!"],
}


def generate_tickets(cfg: GeneratorConfig, n: int = 1_000) -> pl.DataFrame:
    """Generate support tickets with intent and target route.

    Args:
        cfg: Shared generator config (seed and drift are used).
        n: Number of tickets.

    Returns:
        DataFrame with columns ticket_id, intent, route, text.
    """
    rng = np.random.default_rng(cfg.seed + 1)  # different stream than the churn table
    # Drift: more technical/cancellation tickets -> more traffic to the big model.
    p = np.array([0.25, 0.25, 0.2, 0.1, 0.2]) + cfg.drift * np.array([-0.1, -0.05, 0.1, 0.1, -0.05])
    intents = rng.choice(INTENTS, size=n, p=p / p.sum())
    rows = []
    for i, intent in enumerate(intents):
        template = _TEMPLATES[intent][rng.integers(len(_TEMPLATES[intent]))]
        text = template.format(
            order=f"#{rng.integers(10_000, 99_999)}",
            month=rng.choice(["August", "September", "October"]),
            days=int(rng.integers(2, 15)),
            code=f"E{rng.integers(100, 999)}",
            plan=rng.choice(["basic", "plus", "pro"]),
        )
        rows.append(
            {"ticket_id": f"T{i:06d}", "intent": intent, "route": ROUTES[intent], "text": text}
        )
    return pl.DataFrame(rows)
