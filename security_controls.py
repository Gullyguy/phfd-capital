from __future__ import annotations

import ipaddress
import os
import threading
import time
from collections import defaultdict, deque
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status


DEFAULT_ADMIN_PASSWORD = "change-me-now"
MAX_REQUEST_BYTES = int(os.getenv("PHFD_MAX_REQUEST_BYTES", "262144"))
ADMIN_ATTEMPTS = int(os.getenv("PHFD_ADMIN_ATTEMPTS_PER_WINDOW", "10"))
ADMIN_WINDOW_SECONDS = int(os.getenv("PHFD_ADMIN_RATE_WINDOW_SECONDS", "300"))
PUBLIC_SUBMISSIONS = int(os.getenv("PHFD_PUBLIC_SUBMISSIONS_PER_WINDOW", "8"))
PUBLIC_WINDOW_SECONDS = int(os.getenv("PHFD_PUBLIC_RATE_WINDOW_SECONDS", "900"))


class FixedWindowLimiter:
    """Small per-instance limiter. Cloud Armor remains the production edge control."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int, *, record: bool = True) -> int | None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return max(1, int(window_seconds - (now - events[0])))
            if record:
                events.append(now)
        return None


limiter = FixedWindowLimiter()


def validate_production_config(admin_password: str) -> None:
    if os.getenv("K_SERVICE") and admin_password == DEFAULT_ADMIN_PASSWORD:
        raise RuntimeError("Refusing to start Cloud Run with the default admin password")
    if os.getenv("K_SERVICE") and len(admin_password) < 16:
        raise RuntimeError("PHFD_ADMIN_PASSWORD must contain at least 16 characters in production")


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    candidate = forwarded or (request.client.host if request.client else "unknown")
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return "unknown"


def enforce_rate_limit(
    request: Request,
    scope: str,
    limit: int,
    window_seconds: int,
    *,
    record: bool = True,
) -> None:
    retry_after = limiter.check(
        f"{scope}:{client_key(request)}",
        limit,
        window_seconds,
        record=record,
    )
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def enforce_same_origin(request: Request) -> None:
    source = request.headers.get("origin") or request.headers.get("referer")
    if not source:
        raise HTTPException(status_code=403, detail="Request origin required")
    source_url = urlsplit(source)
    expected = request.url
    if source_url.scheme != expected.scheme or source_url.netloc != expected.netloc:
        raise HTTPException(status_code=403, detail="Cross-site admin request blocked")
