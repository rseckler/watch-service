"""
Rate limiting utility for respectful scraping
"""
import time
from datetime import datetime, timedelta
from typing import Dict


class RateLimiter:
    """Rate limiter with per-domain tracking"""

    def __init__(self, default_delay: float = 2.0):
        """
        Initialize rate limiter

        Args:
            default_delay: Default delay in seconds between requests
        """
        self.default_delay = default_delay
        self.last_request: Dict[str, datetime] = {}

    def wait(self, domain: str, delay: float = None):
        """
        Wait if necessary before making request to domain

        Args:
            domain: Domain name (e.g., 'colognewatch.de')
            delay: Optional custom delay (overrides default)
        """
        delay_seconds = delay if delay is not None else self.default_delay

        if domain in self.last_request:
            elapsed = (datetime.now() - self.last_request[domain]).total_seconds()
            remaining = delay_seconds - elapsed

            if remaining > 0:
                time.sleep(remaining)

        self.last_request[domain] = datetime.now()

    def reset(self, domain: str = None):
        """
        Reset rate limiter for domain or all domains

        Args:
            domain: Optional domain to reset (None = reset all)
        """
        if domain:
            self.last_request.pop(domain, None)
        else:
            self.last_request.clear()
