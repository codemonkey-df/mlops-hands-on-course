"""The DCGM mock turns vLLM load into GPU metrics with real DCGM names."""

import pytest
from prometheus_client import CollectorRegistry, generate_latest

from mlops_course.exporters.dcgm_mock import DcgmMockCollector, GpuSpec

IDLE = (
    'vllm:num_requests_running{model_name="m"} 0.0\nvllm:kv_cache_usage_perc{model_name="m"} 0.0\n'
)
BUSY = (
    'vllm:num_requests_running{model_name="m"} 8.0\nvllm:kv_cache_usage_perc{model_name="m"} 1.0\n'
)


def scrape(text: str | None, gpus: int = 1) -> str:
    def fetch() -> str:
        if text is None:
            raise OSError("vLLM not up yet")
        return text

    registry = CollectorRegistry()
    registry.register(DcgmMockCollector(fetch, GpuSpec(count=gpus), max_num_seqs=8))
    return generate_latest(registry).decode()


def value(out: str, metric: str, gpu: str = "0") -> float:
    line = next(
        ln for ln in out.splitlines() if ln.startswith(metric + "{") and f'gpu="{gpu}"' in ln
    )
    return float(line.rsplit(" ", 1)[1])


@pytest.mark.parametrize(
    "name", ["DCGM_FI_DEV_GPU_UTIL", "DCGM_FI_DEV_FB_USED", "DCGM_FI_DEV_GPU_TEMP"]
)
def test_exposes_dcgm_names(name: str) -> None:
    assert name in scrape(IDLE)


def test_load_raises_utilization_and_memory() -> None:
    idle, busy = scrape(IDLE), scrape(BUSY)
    assert value(busy, "DCGM_FI_DEV_GPU_UTIL") > value(idle, "DCGM_FI_DEV_GPU_UTIL")
    assert value(busy, "DCGM_FI_DEV_FB_USED") > value(idle, "DCGM_FI_DEV_FB_USED")


def test_one_series_per_gpu_and_survives_vllm_down() -> None:
    out = scrape(None, gpus=2)
    assert value(out, "DCGM_FI_DEV_GPU_UTIL", gpu="1") == 0
