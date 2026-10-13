"""The client must get predictions back from the deployed service."""
import sys
import urllib.error

from _pyload import fail, load

mod = load(f"{sys.argv[1]}/client.py", "ex_client")
try:
    out = mod.score(mod.customers)
except urllib.error.HTTPError as exc:
    fail(f"HTTP {exc.code}: {exc.read().decode()[:300]}")
print(out)
if len(out.get("predictions", [])) != 2:
    fail("expected 2 predictions")
print("OK")
