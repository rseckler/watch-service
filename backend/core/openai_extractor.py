"""
OpenAI Data Extractor
Uses GPT-4o-mini to extract structured watch data from raw HTML/text
"""

import os
import json
import logging
from openai import OpenAI
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OpenAIExtractor:
    """Extract structured watch data using OpenAI"""

    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        logger.info(f"✓ OpenAI client initialized (model: {self.model})")

    def extract_watch_data(self, raw_text: str, source_name: str, search_criteria: Dict) -> Optional[Dict]:
        """
        Extract structured watch data from raw HTML/text

        Args:
            raw_text: Raw HTML or text content from the listing
            source_name: Name of the source (e.g., "Cologne Watch")
            search_criteria: The search criteria being matched

        Returns:
            Dict with extracted data or None if extraction fails
        """
        try:
            # Truncate text to avoid token limits (keep first 4000 chars)
            truncated_text = raw_text[:4000] if len(raw_text) > 4000 else raw_text

            prompt = self._build_extraction_prompt(truncated_text, source_name, search_criteria)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured data from luxury watch listings. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )

            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)

            # Validate required fields
            if not result.get('manufacturer') or not result.get('model'):
                logger.warning(f"Missing required fields in extraction result")
                return None

            logger.info(f"✓ Extracted data: {result.get('manufacturer')} {result.get('model')} - {result.get('price')} {result.get('currency')}")
            return result

        except Exception as e:
            logger.error(f"✗ OpenAI extraction failed: {e}")
            return None

    def _build_extraction_prompt(self, text: str, source: str, criteria: Dict) -> str:
        """Build the extraction prompt for OpenAI"""
        return f"""Extract structured watch data from this listing text.

Source: {source}
Search Criteria: {criteria.get('manufacturer')} {criteria.get('model')}

Listing Text:
{text}

Extract the following information and return as JSON:
{{
    "manufacturer": "Watch manufacturer (e.g., Rolex, Omega)",
    "model": "Model name (e.g., Submariner, Speedmaster)",
    "reference_number": "Reference/Model number (e.g., 116610LN) or null",
    "year": "Manufacturing year as integer or null",
    "condition": "Condition (Neu, Wie Neu, Sehr Gut, Gut, Gebraucht) or null",
    "price": "Price as number (e.g., 15990) or null",
    "currency": "Currency code (EUR, USD, CHF, GBP) or null",
    "location": "Location/City (e.g., München, Bayern) or null",
    "country": "Country (e.g., Germany, Austria, Switzerland) or null",
    "seller_name": "Seller/Dealer name or null",
    "confidence": "Confidence score 0.0-1.0"
}}

IMPORTANT:
- Normalize manufacturer names (e.g., "ROLEX" → "Rolex")
- Extract only numeric price values (remove currency symbols)
- Extract country from location if possible
- Return null for missing fields
- Ensure JSON is valid"""

    def filter_by_country(self, extracted_data: Dict, allowed_countries: list) -> bool:
        """
        Check if the watch is from an allowed country

        Args:
            extracted_data: Extracted watch data with 'country' field
            allowed_countries: List of allowed country names

        Returns:
            True if country is allowed or unknown, False otherwise
        """
        if not allowed_countries:
            return True  # No country restriction

        country = extracted_data.get('country', '').strip()

        if not country:
            # Country unknown - allow it (user can manually check)
            return True

        # Normalize country names for comparison
        country_lower = country.lower()
        allowed_lower = [c.lower() for c in allowed_countries]

        # Check if country is in allowed list
        for allowed in allowed_lower:
            if allowed in country_lower or country_lower in allowed:
                return True

        logger.info(f"✗ Filtered out: {country} not in allowed countries {allowed_countries}")
        return False

    def match_search_criteria(self, extracted_data: Dict, search_criteria: Dict) -> bool:
        """
        Check if extracted data matches the search criteria

        Args:
            extracted_data: Extracted watch data
            search_criteria: Search criteria from database

        Returns:
            True if data matches criteria (fuzzy matching)
        """
        # Check manufacturer
        extracted_mfr = extracted_data.get('manufacturer', '').lower()
        criteria_mfr = search_criteria.get('manufacturer', '').lower()

        if criteria_mfr not in extracted_mfr and extracted_mfr not in criteria_mfr:
            return False

        # Check model
        extracted_model = extracted_data.get('model', '').lower()
        criteria_model = search_criteria.get('model', '').lower()

        if criteria_model not in extracted_model and extracted_model not in criteria_model:
            return False

        # Optional: Check reference number if specified
        criteria_ref = search_criteria.get('reference_number')
        if criteria_ref:
            extracted_ref = extracted_data.get('reference_number', '')
            if extracted_ref and criteria_ref.lower() not in extracted_ref.lower():
                return False

        return True
