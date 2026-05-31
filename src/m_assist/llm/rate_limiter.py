"""
rate_limiter.py — a simple sliding-window rate limiter.

Tracks request timestamps and tells you whether a new request would
exceed the per-minute or per-day cap. We use this BEFORE calling a
cloud API so we can fail over proactively instead of waiting for a 429.
"""

import time
from collections import deque


class RateLimiter:
    """Sliding-window limiter for requests-per-minute and per-day.

    We don't enforce tokens-per-minute precisely here (we don't know
    token count until after the call); RPM/RPD are the limits you
    actually hit first in practice.
    """

    def __init__(self, requests_per_minute: int, requests_per_day: int):
        self.rpm = requests_per_minute
        self.rpd = requests_per_day
        # deques of timestamps (seconds). Left = oldest.
        self._minute = deque()
        self._day = deque()

    def _prune(self, now: float) -> None:
        # Drop timestamps outside their window.
        while self._minute and now - self._minute[0] > 60:
            self._minute.popleft()
        while self._day and now - self._day[0] > 86400:
            self._day.popleft()

    def allow(self) -> bool:
        """Return True if a request is allowed right now, else False."""
        now = time.time()
        self._prune(now)
        return len(self._minute) < self.rpm and len(self._day) < self.rpd

    def record(self) -> None:
        """Call this right after a successful request."""
        now = time.time()
        self._minute.append(now)
        self._day.append(now)

    def status(self) -> str:
        now = time.time()
        self._prune(now)
        return f"{len(self._minute)}/{self.rpm} per-min, {len(self._day)}/{self.rpd} per-day"