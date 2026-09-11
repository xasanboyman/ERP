import threading
from cachetools import TTLCache
from typing import Any, Optional

_lock = threading.Lock()

# 24-hour TTL for aggregated analytics data (auto-invalidated on mutations)
_analytics_cache = TTLCache(maxsize=512, ttl=86400)

# 10-minute TTL for sales list queries (auto-invalidated on new checkout)
_sales_cache = TTLCache(maxsize=512, ttl=600)

def get_analytics_cache(key: str) -> Optional[Any]:
    with _lock:
        return _analytics_cache.get(key)

def set_analytics_cache(key: str, value: Any):
    with _lock:
        _analytics_cache[key] = value

def get_sales_cache(key: str) -> Optional[Any]:
    with _lock:
        return _sales_cache.get(key)

def set_sales_cache(key: str, value: Any):
    with _lock:
        _sales_cache[key] = value

def invalidate_analytics():
    with _lock:
        _analytics_cache.clear()

def invalidate_sales():
    with _lock:
        _sales_cache.clear()

def invalidate_all():
    with _lock:
        _analytics_cache.clear()
        _sales_cache.clear()
