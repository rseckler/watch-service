"""
Text processing utilities for watch data
"""
import re
import hashlib
from typing import Optional


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace and trimming

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_price(text: str) -> Optional[float]:
    """
    Extract numeric price from text

    Args:
        text: Text containing price (e.g., "€ 5.999,00", "5999 EUR")

    Returns:
        Price as float or None if not found
    """
    if not text:
        return None

    # Remove currency symbols and whitespace
    text = re.sub(r'[€$£¥]', '', text)
    text = text.strip()

    # Handle European format (5.999,00) -> 5999.00
    if ',' in text and '.' in text:
        text = text.replace('.', '').replace(',', '.')
    # Handle European format without thousands separator (5999,00)
    elif ',' in text:
        text = text.replace(',', '.')

    # Extract first number
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None

    return None


def extract_currency(text: str) -> str:
    """
    Extract currency from text

    Args:
        text: Text containing currency

    Returns:
        Currency code (EUR, USD, CHF, GBP) or 'EUR' as default
    """
    if not text:
        return 'EUR'

    text = text.upper()

    if '€' in text or 'EUR' in text:
        return 'EUR'
    elif '$' in text or 'USD' in text:
        return 'USD'
    elif 'CHF' in text or 'SFR' in text:
        return 'CHF'
    elif '£' in text or 'GBP' in text:
        return 'GBP'

    return 'EUR'  # Default


def generate_url_hash(url: str) -> str:
    """
    Generate short hash for URL (for duplicate detection)

    Args:
        url: Full URL

    Returns:
        SHA256 hash (first 16 characters)
    """
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def normalize_manufacturer(manufacturer: str) -> str:
    """
    Normalize manufacturer name

    Args:
        manufacturer: Raw manufacturer name

    Returns:
        Normalized manufacturer name
    """
    if not manufacturer:
        return ""

    # Common normalizations
    manufacturer = manufacturer.strip().title()

    # Special cases
    replacements = {
        'A. Lange & Söhne': 'A. Lange & Sohne',
        'A Lange': 'A. Lange & Sohne',
        'Iwc': 'IWC',
        'Ap': 'Audemars Piguet',
        'Pp': 'Patek Philippe',
        'Vc': 'Vacheron Constantin',
        'Jlc': 'Jaeger-LeCoultre',
    }

    for old, new in replacements.items():
        if manufacturer.lower() == old.lower():
            return new

    return manufacturer


def truncate_html(html: str, max_length: int = 4000) -> str:
    """
    Truncate HTML to reduce OpenAI token usage

    Args:
        html: Raw HTML
        max_length: Maximum character length

    Returns:
        Truncated HTML
    """
    if len(html) <= max_length:
        return html

    return html[:max_length] + "..."
