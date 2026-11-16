import time
from collections import defaultdict
from typing import Dict, List
from backend.app.core.config import settings


class SessionRateLimiter:
    """
    Sliding window rate limiter tracking request timestamps per session.
    """
    def __init__(self, max_requests: int = None, window_seconds: int = 60):
        self.max_requests = max_requests or settings.RATE_LIMIT_MESSAGES_PER_MINUTE
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, session_id: str) -> bool:
        now = time.time()
        timestamps = self.history[session_id]
        
        # Prune expired timestamps outside the rolling window
        valid_timestamps = [ts for ts in timestamps if now - ts < self.window_seconds]
        self.history[session_id] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            return False

        self.history[session_id].append(now)
        return True

    def reset_session(self, session_id: str):
        if session_id in self.history:
            del self.history[session_id]


rate_limiter = SessionRateLimiter()
