"""
GAME CHANGER: Generic scraper that reads configuration from Notion Sources DB
Eliminates need for custom scrapers for 80% of sources
"""
import os
from typing import List, Dict, Any
from urllib.parse import urljoin
from .base_scraper import BaseScraper
from .static_scraper import StaticScraper
from .dynamic_scraper import DynamicScraper
from utils.logger import get_logger

logger = get_logger(__name__)


class GenericScraper(BaseScraper):
    """
    Intelligent scraper that reads CSS selectors from Notion configuration
    No code changes needed to add new sources!
    """

    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize generic scraper with Notion source config

        Args:
            source_config: Configuration from Notion Sources DB with:
                - Name, URL, Domain, Type, Scraper_Type
                - Search_URL_Template, Listing_Selector, etc.
                - Rate_Limit_Seconds
        """
        super().__init__(source_config)

        self.scraper_type = source_config.get('Scraper_Type', 'Static')
        self.search_url_template = source_config.get('Search_URL_Template', '')
        self.listing_selector = source_config.get('Listing_Selector', '')
        self.title_selector = source_config.get('Title_Selector', '')
        self.price_selector = source_config.get('Price_Selector', '')
        self.link_selector = source_config.get('Link_Selector', '')
        self.image_selector = source_config.get('Image_Selector', '')

        # Initialize appropriate engine
        if self.scraper_type == 'Dynamic':
            self.engine = DynamicScraper(self.domain, self.rate_limit)
            logger.info(f"Initialized Dynamic scraper for {self.source_name}")
        else:
            # Default to static scraper
            self.engine = StaticScraper(self.domain, self.rate_limit)
            logger.info(f"Initialized Static scraper for {self.source_name}")

    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for watches using configured selectors

        Args:
            criteria: Search criteria with Manufacturer, Model, etc.

        Returns:
            List of raw listings
        """
        try:
            # Build search URL from template
            search_url = self._build_search_url(criteria)
            if not search_url:
                logger.warning(f"No search URL template configured for {self.source_name}")
                return []

            logger.info(f"Searching {self.source_name}: {search_url}")

            # Fetch page using configured engine
            soup = self.engine.fetch_page(search_url)

            # Extract listings using CSS selectors
            listings = self._extract_listings(soup)

            logger.info(f"Found {len(listings)} listings from {self.source_name}")
            return listings

        except Exception as e:
            logger.error(f"Search failed for {self.source_name}: {e}")
            return []

    def _build_search_url(self, criteria: Dict[str, Any]) -> str:
        """
        Build search URL from template and criteria

        Args:
            criteria: Search criteria

        Returns:
            Formatted search URL
        """
        if not self.search_url_template:
            return ""

        manufacturer = criteria.get('Manufacturer', '').strip()
        model = criteria.get('Model', '').strip()

        # Replace placeholders in template
        url = self.search_url_template
        url = url.replace('{manufacturer}', manufacturer)
        url = url.replace('{model}', model)
        url = url.replace('{Manufacturer}', manufacturer)
        url = url.replace('{Model}', model)

        # URL encode spaces
        url = url.replace(' ', '+')

        return url

    def _extract_listings(self, soup) -> List[Dict[str, Any]]:
        """
        Extract listings from page using CSS selectors

        Args:
            soup: BeautifulSoup object

        Returns:
            List of raw listings
        """
        listings = []

        if not self.listing_selector:
            logger.warning(f"No listing selector configured for {self.source_name}")
            return []

        # Find all listing containers
        listing_elements = soup.select(self.listing_selector)

        for element in listing_elements:
            try:
                listing = self._extract_single_listing(element)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to extract listing: {e}")
                continue

        return listings

    def _extract_single_listing(self, element) -> Dict[str, Any]:
        """
        Extract data from single listing element

        Args:
            element: BeautifulSoup element

        Returns:
            Listing dictionary or None if extraction failed
        """
        # Extract title
        title = ""
        if self.title_selector:
            title_elem = element.select_one(self.title_selector)
            if title_elem:
                title = title_elem.get_text(strip=True)

        # Extract price
        price_text = ""
        if self.price_selector:
            price_elem = element.select_one(self.price_selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)

        # Extract link
        link = ""
        if self.link_selector:
            link_elem = element.select_one(self.link_selector)
            if link_elem:
                link = link_elem.get('href', '')
                # Make absolute URL if relative
                if link and not link.startswith('http'):
                    base_url = self.config.get('URL', '')
                    link = urljoin(base_url, link)

        # Validation
        if not title and not link:
            return None

        # Build listing
        listing = {
            'title': title,
            'price': price_text,
            'link': link,
            'raw_html': str(element),
            'source_name': self.source_name,
            'source_type': self.config.get('Type', 'Unknown')
        }

        return listing

    def check_availability(self, url: str) -> bool:
        """
        Check if listing is still available

        Args:
            url: Listing URL

        Returns:
            True if available
        """
        try:
            return self.engine.check_availability(url)
        except Exception as e:
            logger.error(f"Availability check failed: {e}")
            return False

    def close_driver(self):
        """Close underlying engine"""
        try:
            self.engine.close()
        except Exception as e:
            logger.error(f"Error closing engine: {e}")


class CustomScraperLoader:
    """
    Loads custom scrapers for complex sources
    Falls back to GenericScraper if custom scraper not needed
    """

    @staticmethod
    def load_scraper(source_config: Dict[str, Any]) -> BaseScraper:
        """
        Load appropriate scraper for source

        Args:
            source_config: Source configuration from Notion

        Returns:
            Scraper instance (custom or generic)
        """
        custom_scraper = source_config.get('Custom_Scraper', '').strip()

        if custom_scraper:
            # Try to load custom scraper
            try:
                module_name = custom_scraper.replace('.py', '')
                module_path = f"sources.custom.{module_name}"

                # Dynamic import
                import importlib
                module = importlib.import_module(module_path)

                # Instantiate scraper class (assume class name = module name in PascalCase)
                class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                scraper_class = getattr(module, class_name)

                logger.info(f"Loading custom scraper: {custom_scraper}")
                return scraper_class(source_config)

            except Exception as e:
                logger.warning(f"Failed to load custom scraper {custom_scraper}: {e}")
                logger.info(f"Falling back to GenericScraper for {source_config.get('Name')}")

        # Use generic scraper
        return GenericScraper(source_config)
