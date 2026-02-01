"""
Abstract base class for all scrapers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from utils.text_utils import generate_url_hash


class BaseScraper(ABC):
    """Abstract base scraper interface"""

    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize scraper with source configuration

        Args:
            source_config: Source configuration from Notion Sources DB
        """
        self.config = source_config
        self.source_name = source_config.get('Name', 'Unknown')
        self.domain = source_config.get('Domain', '')
        self.rate_limit = source_config.get('Rate_Limit_Seconds', 2)

    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for watches matching criteria

        Args:
            criteria: Search criteria from Notion

        Returns:
            List of raw listings with keys:
                - title: Watch title
                - price: Price text
                - link: Full URL to listing
                - raw_html: Raw HTML of listing
                - source_name: Source name
                - source_type: Source type (Dealer/Forum/Marketplace)
        """
        pass

    @abstractmethod
    def check_availability(self, url: str) -> bool:
        """
        Check if listing is still available

        Args:
            url: Full URL to listing

        Returns:
            True if listing is still available, False if sold/removed
        """
        pass

    def generate_url_hash(self, url: str) -> str:
        """
        Generate hash for URL (for duplicate detection)

        Args:
            url: Full URL

        Returns:
            SHA256 hash (first 16 characters)
        """
        return generate_url_hash(url)

    def close_driver(self):
        """
        Close any open browser drivers (for Selenium scrapers)
        Base implementation does nothing - override if needed
        """
        pass
