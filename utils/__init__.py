"""Utilities package"""
from .logger import setup_logger, get_logger
from .rate_limiter import RateLimiter
from .text_utils import (
    normalize_text,
    extract_price,
    extract_currency,
    generate_url_hash,
    normalize_manufacturer,
    truncate_html
)

__all__ = [
    'setup_logger',
    'get_logger',
    'RateLimiter',
    'normalize_text',
    'extract_price',
    'extract_currency',
    'generate_url_hash',
    'normalize_manufacturer',
    'truncate_html'
]
