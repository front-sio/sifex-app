from typing import Any


def increment(metric_name: str, value: int = 1, **tags: Any) -> None:
    """Placeholder for metrics counters."""
    _ = (metric_name, value, tags)


def observe(metric_name: str, value: float, **tags: Any) -> None:
    """Placeholder for metrics latency observations."""
    _ = (metric_name, value, tags)
