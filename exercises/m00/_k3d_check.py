"""Static checks for a k3d Simple config, shared by the M0 exercises.

Usage: python _k3d_check.py <cluster.yaml.tpl> <check-name>
"""

import sys

import yaml


def load(path: str) -> dict:
    with open(path) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        sys.exit("FAIL: file is not a YAML mapping")
    return data


def check_structure(cfg: dict) -> None:
    for key in ("apiVersion", "kind", "metadata", "servers", "agents", "ports", "options"):
        if key not in cfg:
            sys.exit(f"FAIL: top-level key '{key}' missing (wrong indentation?)")
    if not isinstance(cfg["ports"], list):
        sys.exit("FAIL: 'ports' must be a list")


def check_kmsg(cfg: dict) -> None:
    for vol in cfg.get("volumes", []):
        if vol.get("volume", "").endswith(":/dev/kmsg"):
            filters = " ".join(vol.get("nodeFilters", []))
            if "server:*" in filters and "agent:*" in filters:
                return
            sys.exit(f"FAIL: /dev/kmsg workaround only applied to {filters!r}")
    sys.exit("FAIL: no /dev/kmsg volume")


def check_ingress_port(cfg: dict) -> None:
    for port in cfg.get("ports", []):
        if port.get("port", "").endswith(":80"):
            if port.get("nodeFilters") == ["loadbalancer"]:
                return
            sys.exit(f"FAIL: port 80 is bound to {port.get('nodeFilters')}, not the loadbalancer")
    sys.exit("FAIL: no host port mapped to 80")


CHECKS = {"structure": check_structure, "kmsg": check_kmsg, "ingress": check_ingress_port}

if __name__ == "__main__":
    config = load(sys.argv[1])
    check_structure(config)
    CHECKS[sys.argv[2]](config)
    print("OK")
