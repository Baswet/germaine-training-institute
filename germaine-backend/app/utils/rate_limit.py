"""
Small in-process sliding-window rate limiter (no new dependency).

Used by the public lead-capture endpoint to throttle automated spam. It is
per worker process: under Passenger with N worker processes the effective
ceiling is up to N x the configured limit. That is an acceptable bound for
spam throttling (the lead token's UNIQUE constraint is what actually
prevents duplicates); a shared limiter (Redis etc.) would be a new piece of
infrastructure and is deliberately not introduced here.

The client IP is used only as an in-memory throttling key and is never
written to the database or logs.
"""

import threading
import time
from collections import deque


class SlidingWindowLimiter:
    def __init__(self, max_events: int, window_seconds: float, max_keys: int = 20000):
        self.max_events = max_events
        self.window = window_seconds
        self.max_keys = max_keys
        self._events: dict[str, deque] = {}
        self._lock = threading.Lock()

    def hit(self, key: str) -> bool:
        """Record an event for `key`; return False if it exceeds the limit."""
        now = time.monotonic()
        cutoff = now - self.window
        with self._lock:
            if len(self._events) > self.max_keys:
                self._prune(cutoff)
            q = self._events.setdefault(key, deque())
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.max_events:
                return False
            q.append(now)
            return True

    def reset(self):
        with self._lock:
            self._events.clear()

    def _prune(self, cutoff):
        for k in [k for k, q in self._events.items() if not q or q[-1] < cutoff]:
            del self._events[k]
