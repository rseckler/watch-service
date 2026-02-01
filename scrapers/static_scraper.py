"""
Static scraper using BeautifulSoup for simple HTML pages
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class StaticScraper:
    """Scraper for static HTML pages using requests + BeautifulSoup"""

    def __init__(self, domain: str, rate_limit: float = 2.0):
        """
        Initialize static scraper

        Args:
            domain: Domain name (for rate limiting)
            rate_limit: Seconds between requests
        """
        self.domain = domain
        self.rate_limiter = RateLimiter(default_delay=rate_limit)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_page(self, url: str) -> BeautifulSoup:
        """
        Fetch page and return BeautifulSoup object

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object

        Raises:
            requests.RequestException on failure
        """
        self.rate_limiter.wait(self.domain)

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        return BeautifulSoup(response.content, 'lxml')

    def check_availability(self, url: str) -> bool:
        """
        Check if URL is still accessible

        Args:
            url: URL to check

        Returns:
            True if page loads successfully (status 200)
        """
        try:
            self.rate_limiter.wait(self.domain)
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False

    def close(self):
        """Close session"""
        self.session.close()
