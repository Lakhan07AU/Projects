"""Simple in-process rate limiter (token bucket per key).

For multi-instance production deployments, back this with Redis.
"""
import threading
import time
from collections import defaultdict

from app.core.errors import RateLimitError

_lock = threading.Lock()
_buckets: dict[str, list[float]] = defaultdict(list)


def rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    now = time.monotonic()
    with _lock:
        window_start = now - window_seconds
        hits = [t for t in _buckets[key] if t > window_start]
        if len(hits) >= max_requests:
            raise RateLimitError()
        hits.append(now)
        _buckets[key] = hits


def clear_rate_limits() -> None:
    with _lock:
        _buckets.clear()
