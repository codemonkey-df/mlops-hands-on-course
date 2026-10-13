"""Fake NVIDIA DCGM exporter: GPU metrics derived from the local vLLM's load.

Real clusters run NVIDIA's dcgm-exporter as a DaemonSet on every GPU node
(port 9400). This mock runs as a sidecar next to the mock vLLM, reads its
/metrics on every scrape and reports a "GPU" that gets busy when vLLM does.
Metric and label names match dcgm-exporter, so dashboards work on both.

    python -m mlops_course.exporters.dcgm_mock --vllm-url http://localhost:8000/metrics
"""

import argparse
import logging
import socket
import time
import urllib.request
from collections.abc import Callable, Iterator

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily, Metric
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.registry import Collector
from pydantic import BaseModel

logger = logging.getLogger(__name__)

LABELS = ["gpu", "UUID", "device", "modelName", "Hostname"]


class GpuSpec(BaseModel):
    """What the fake GPUs look like."""

    count: int = 1
    model_name: str = "NVIDIA RTX 4070 Ti SUPER (mock)"
    memory_mib: int = 16376


class DcgmMockCollector(Collector):
    """Custom collector: computes the values at scrape time (no background thread)."""

    def __init__(self, fetch: Callable[[], str], gpus: GpuSpec, max_num_seqs: int) -> None:
        self._fetch = fetch
        self._gpus = gpus
        self._max_num_seqs = max_num_seqs
        self._host = socket.gethostname()

    def _vllm_load(self) -> tuple[float, float]:
        """(running sequences, KV-cache usage 0..1) from vLLM; zeros if it's not up."""
        try:
            text = self._fetch()
        except OSError:
            return 0.0, 0.0
        values: dict[str, float] = {}
        for family in text_string_to_metric_families(text):
            for sample in family.samples:
                values[sample.name] = values.get(sample.name, 0.0) + sample.value
        return values.get("vllm:num_requests_running", 0.0), values.get(
            "vllm:kv_cache_usage_perc", 0.0
        )

    def collect(self) -> Iterator[Metric]:
        """Yield one sample per fake GPU for each DCGM metric."""
        running, kv = self._vllm_load()
        busy = min(1.0, running / self._max_num_seqs)
        mem = self._gpus.memory_mib
        # vLLM pre-allocates ~90% of memory for weights + KV cache at startup,
        # so memory is high even when idle; that's normal, not a leak.
        used = mem * (0.85 + 0.05 * kv)
        metrics = {
            "DCGM_FI_DEV_GPU_UTIL": ("GPU utilization (in %).", 3 + 95 * busy),
            "DCGM_FI_DEV_FB_USED": ("Framebuffer memory used (in MiB).", used),
            "DCGM_FI_DEV_FB_FREE": ("Framebuffer memory free (in MiB).", mem - used),
            "DCGM_FI_DEV_GPU_TEMP": ("GPU temperature (in C).", 38 + 40 * busy),
            "DCGM_FI_DEV_POWER_USAGE": ("Power draw (in W).", 25 + 260 * busy),
        }
        for name, (doc, val) in metrics.items():
            g = GaugeMetricFamily(name, doc, labels=LABELS)
            for i in range(self._gpus.count):
                labels = [
                    str(i),
                    f"GPU-mock-{self._host}-{i}",
                    f"nvidia{i}",
                    self._gpus.model_name,
                    self._host,
                ]
                g.add_metric(labels, val if running or name != "DCGM_FI_DEV_GPU_UTIL" else 0.0)
            yield g


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--vllm-url", default="http://localhost:8000/metrics")
    p.add_argument("--gpus", type=int, default=1)
    p.add_argument("--max-num-seqs", type=int, default=8)
    p.add_argument("--port", type=int, default=9400)  # dcgm-exporter's port
    args = p.parse_args()

    def fetch() -> str:
        with urllib.request.urlopen(args.vllm_url, timeout=2) as r:
            return str(r.read().decode())

    REGISTRY.register(DcgmMockCollector(fetch, GpuSpec(count=args.gpus), args.max_num_seqs))
    start_http_server(args.port)
    logger.info("dcgm mock on :%d, reading %s", args.port, args.vllm_url)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
