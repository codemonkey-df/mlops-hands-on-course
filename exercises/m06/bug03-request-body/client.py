"""Minimal client app: score two customers through the Ingress."""

import json
import urllib.request

URL = "http://churn.192.168.1.202.nip.io:8080/predict"

customers = [
    {"customer_id": "C1", "plan": "basic", "region": "north", "tenure_months": 2,
     "monthly_spend": 15.0, "support_tickets_90d": 6, "days_since_last_order": 60,
     "app_sessions_30d": 1, "discount_used": False},
    {"customer_id": "C2", "plan": "pro", "region": "west", "tenure_months": 40,
     "monthly_spend": 120.0, "support_tickets_90d": 0, "days_since_last_order": 3,
     "app_sessions_30d": 40, "discount_used": True},
]


def score(batch: list[dict[str, object]]) -> dict[str, object]:
    body = json.dumps({"customers": batch}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


if __name__ == "__main__":
    print(json.dumps(score(customers), indent=2))
