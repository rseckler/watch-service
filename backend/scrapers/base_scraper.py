"""
Base Scraper Class
Abstract base class for all watch source scrapers
"""

import hashlib
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for watch scrapers"""

    def __init__(self, source_name: str, source_url: str, rate_limit: int = 2):
        """
        Initialize scraper

        Args:
            source_name: Display name of the source
            source_url: Base URL of the source
            rate_limit: Seconds to wait between requests
        """
        self.source_name = source_name
        self.source_url = source_url
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info(f"✓ Initialized scraper: {source_name}")

    @abstractmethod
    def search(self, search_criteria: Dict) -> List[Dict]:
        """
        Search for watches matching the criteria

        Args:
            search_criteria: Dict with manufacturer, model, reference_number, etc.

        Returns:
            List of raw listings (dicts with 'title', 'link', 'raw_html', etc.)
        """
        pass

    def fetch_page(self, url: str, method: str = 'GET', **kwargs) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return BeautifulSoup object

        Args:
            url: URL to fetch
            method: HTTP method (GET or POST)
            **kwargs: Additional arguments for requests

        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            # Rate limiting
            time.sleep(self.rate_limit)

            # Make request
            if method == 'GET':
                response = self.session.get(url, timeout=30, **kwargs)
            else:
                response = self.session.post(url, timeout=30, **kwargs)

            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')
            logger.debug(f"✓ Fetched: {url}")
            return soup

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to fetch {url}: {e}")
            return None

    def generate_url_hash(self, url: str) -> str:
        """
        Generate a unique hash for a URL (for duplicate detection)

        Args:
            url: The listing URL

        Returns:
            SHA256 hash (truncated to 16 chars)
        """
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def check_availability(self, url: str) -> bool:
        """
        Check if a listing is still available

        Args:
            url: The listing URL

        Returns:
            True if available, False if sold/removed
        """
        try:
            # Rate limiting
            time.sleep(self.rate_limit)

            response = self.session.head(url, timeout=10, allow_redirects=True)

            # If we get 404 or 410, it's definitely gone
            if response.status_code in [404, 410]:
                return False

            # If we get 200, fetch the page and check for "sold" indicators
            if response.status_code == 200:
                soup = self.fetch_page(url)
                if soup:
                    text_lower = soup.get_text().lower()
                    # Common "sold" indicators
                    sold_indicators = ['verkauft', 'sold', 'nicht verfügbar', 'out of stock']
                    for indicator in sold_indicators:
                        if indicator in text_lower:
                            return False

            return True

        except Exception as e:
            logger.warning(f"Could not check availability for {url}: {e}")
            # If we can't check, assume it's still available
            return True

    def close(self):
        """Close the scraper session"""
        self.session.close()
        logger.debug(f"Closed scraper: {self.source_name}")
