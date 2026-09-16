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

# 1-hour TTL for authenticated user records and password hashes
_user_auth_cache = TTLCache(maxsize=256, ttl=3600)

# 1-hour TTL for user route menus
_role_menu_cache = TTLCache(maxsize=128, ttl=3600)

# 30-minute TTL for employee lists
_employee_cache = TTLCache(maxsize=16, ttl=1800)

# 1-hour TTL for branch lists
_branch_cache = TTLCache(maxsize=16, ttl=3600)

def get_user_auth_cache(username: str) -> Optional[dict]:
    with _lock:
        return _user_auth_cache.get(username.lower().strip())

def set_user_auth_cache(username: str, data: dict):
    with _lock:
        _user_auth_cache[username.lower().strip()] = data

def get_role_menu_cache(role_name: str) -> Optional[Any]:
    with _lock:
        return _role_menu_cache.get(role_name.lower().strip())

def set_role_menu_cache(role_name: str, data: Any):
    with _lock:
        _role_menu_cache[role_name.lower().strip()] = data

def get_employee_cache() -> Optional[Any]:
    with _lock:
        return _employee_cache.get("all_employees")

def set_employee_cache(data: Any):
    with _lock:
        _employee_cache["all_employees"] = data

def get_branch_cache() -> Optional[Any]:
    with _lock:
        return _branch_cache.get("all_branches")

def set_branch_cache(data: Any):
    with _lock:
        _branch_cache["all_branches"] = data

def invalidate_auth():
    with _lock:
        _user_auth_cache.clear()
        _role_menu_cache.clear()
        _employee_cache.clear()

def invalidate_branches():
    with _lock:
        _branch_cache.clear()
