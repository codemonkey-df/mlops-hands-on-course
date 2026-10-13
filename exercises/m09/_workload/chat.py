"""One chat request through the router at localhost:4000 (run inside the pod)."""

import json
import os
import sys
import urllib.error
import urllib.request

body = {"model": sys.argv[1], "max_tokens": 8, "messages": [{"role": "user", "content": "hi"}]}
req = urllib.request.Request(
    "http://localhost:4000/v1/chat/completions",
    json.dumps(body).encode(),
    {"Authorization": "Bearer " + os.environ["LITELLM_MASTER_KEY"], "Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
        print(d["model"], d["choices"][0]["message"]["content"])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:400]}")
    sys.exit(1)
