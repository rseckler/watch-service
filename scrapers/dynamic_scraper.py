"""
Dynamic scraper using Selenium for JavaScript-heavy pages
"""
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from typing import Optional
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class DynamicScraper:
    """Scraper for JavaScript-heavy pages using Selenium"""

    def __init__(self, domain: str, rate_limit: float = 3.0):
        """
        Initialize dynamic scraper with Selenium

        Args:
            domain: Domain name (for rate limiting)
            rate_limit: Seconds between requests
        """
        self.domain = domain
        self.rate_limiter = RateLimiter(default_delay=rate_limit)
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            options = Options()

            # Headless mode from env
            if os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true':
                options.add_argument('--headless=new')

            # Common options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

            # Disable images for faster loading
            prefs = {'profile.managed_default_content_settings.images': 2}
            options.add_experimental_option('prefs', prefs)

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)

            logger.info("Selenium WebDriver initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            raise

    def fetch_page(self, url: str, wait_for_selector: str = None) -> BeautifulSoup:
        """
        Fetch page with Selenium and return BeautifulSoup object

        Args:
            url: URL to fetch
            wait_for_selector: Optional CSS selector to wait for before returning

        Returns:
            BeautifulSoup object

        Raises:
            WebDriverException on failure
        """
        if not self.driver:
            self._init_driver()

        self.rate_limiter.wait(self.domain)

        try:
            self.driver.get(url)

            # Wait for specific element if specified
            if wait_for_selector:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
            else:
                # Default wait for page load
                time.sleep(2)

            # Get page source
            html = self.driver.page_source
            return BeautifulSoup(html, 'lxml')

        except TimeoutException:
            logger.warning(f"Timeout waiting for {wait_for_selector}")
            # Return what we have
            return BeautifulSoup(self.driver.page_source, 'lxml')

        except Exception as e:
            logger.error(f"Selenium fetch failed: {e}")
            raise

    def check_availability(self, url: str) -> bool:
        """
        Check if URL is still accessible

        Args:
            url: URL to check

        Returns:
            True if page loads successfully
        """
        try:
            if not self.driver:
                self._init_driver()

            self.rate_limiter.wait(self.domain)
            self.driver.get(url)
            time.sleep(1)

            # Check if we got redirected to error page or homepage
            current_url = self.driver.current_url
            if url not in current_url and self.domain not in current_url:
                return False

            return True

        except Exception:
            return False

    def close(self):
        """Close WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
