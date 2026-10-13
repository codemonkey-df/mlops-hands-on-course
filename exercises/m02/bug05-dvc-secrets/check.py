"""`config` (committed) must hold no credentials; `config.local` (git-ignored) must."""
import configparser
import sys

from _pyload import fail

d = sys.argv[1]
shared, local = configparser.ConfigParser(), configparser.ConfigParser()
shared.read(f"{d}/config")
local.read(f"{d}/config.local")
sec = "'remote \"minio\"'"
for key in ("access_key_id", "secret_access_key"):
    if shared.has_option(sec, key):
        fail(f"{key} is in .dvc/config, which is committed to git")
    if not local.has_option(sec, key):
        fail(f"{key} missing from .dvc/config.local: dvc push would have no credentials")
for key in ("url", "endpointurl"):
    if not shared.has_option(sec, key):
        fail(f"{key} must stay in the shared config so teammates get it")
print("OK")
