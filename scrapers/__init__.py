"""Scrapers package"""
from .base_scraper import BaseScraper
from .static_scraper import StaticScraper
from .dynamic_scraper import DynamicScraper
from .generic_scraper import GenericScraper, CustomScraperLoader

__all__ = [
    'BaseScraper',
    'StaticScraper',
    'DynamicScraper',
    'GenericScraper',
    'CustomScraperLoader'
]
