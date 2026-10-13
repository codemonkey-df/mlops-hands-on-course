"""Load a Python file from an exercise folder as a module (no package needed)."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load(path: str | Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)
