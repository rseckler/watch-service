"""
OpenAI GPT-4o-mini integration for extracting structured watch data
"""
import os
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from utils.logger import get_logger
from utils.text_utils import truncate_html, normalize_manufacturer

logger = get_logger(__name__)


class OpenAIExtractor:
    """Extract structured watch data from HTML using OpenAI"""

    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.confidence_threshold = float(os.getenv('OPENAI_CONFIDENCE_THRESHOLD', '0.5'))

    def extract_watch_data(self, raw_html: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured watch data from raw HTML

        Args:
            raw_html: Raw HTML content from listing
            source_name: Source website name (for context)

        Returns:
            Dictionary with extracted data or None if extraction failed
        """
        try:
            # Truncate HTML to reduce token usage
            html = truncate_html(raw_html, max_length=4000)

            system_prompt = """Du bist ein Experte für Luxusuhren-Datenextraktion.

Deine Aufgabe ist es, strukturierte Daten aus HTML-Einträgen von Uhren-Angeboten zu extrahieren.

Extrahiere folgende Informationen:
- manufacturer: Hersteller (z.B. "Rolex", "Omega", "Patek Philippe")
- model: Modellname (z.B. "Submariner", "Speedmaster")
- reference_number: Referenznummer falls vorhanden (z.B. "116610LN")
- year: Herstellungsjahr falls angegeben (als Zahl)
- condition: Zustand (wähle aus: "Neu", "Wie Neu", "Sehr Gut", "Gut", "Gebraucht", "Unbekannt")
- price: Preis als Zahl (nur die Zahl, ohne Währungssymbol)
- currency: Währung (EUR, USD, CHF, oder GBP)
- location: Standort/Stadt des Verkäufers
- country: Land des Verkäufers (Deutschland, Österreich, Schweiz, etc.)
- seller_name: Name des Verkäufers/Händlers
- confidence: Dein Konfidenzwert 0.0-1.0 wie sicher du bei der Extraktion bist

Wichtig:
- Normalisiere Herstellernamen (z.B. "ROLEX" → "Rolex")
- Extrahiere nur numerische Preise (z.B. "5.999,00 €" → 5999.00)
- Wenn eine Information nicht verfügbar ist, setze sie auf null
- Sei konservativ mit der Konfidenz - nur > 0.8 wenn sehr sicher

Antworte NUR mit validem JSON, keine zusätzlichen Erklärungen."""

            user_prompt = f"""Quelle: {source_name}

HTML-Inhalt:
{html}

Extrahiere die Uhrendaten als JSON."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent extraction
            )

            # Parse JSON response
            result = json.loads(response.choices[0].message.content)

            # Validate confidence
            confidence = result.get('confidence', 0)
            if confidence < self.confidence_threshold:
                logger.warning(f"Low confidence extraction: {confidence:.2f} < {self.confidence_threshold}")
                return None

            # Normalize manufacturer
            if result.get('manufacturer'):
                result['manufacturer'] = normalize_manufacturer(result['manufacturer'])

            logger.info(f"Extracted watch data with confidence {confidence:.2f}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            return None

    def match_search_criteria(
        self,
        extracted: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> bool:
        """
        Check if extracted watch matches search criteria (fuzzy matching)

        Args:
            extracted: Extracted watch data
            criteria: Search criteria

        Returns:
            True if watch matches criteria
        """
        # Manufacturer must match (case-insensitive, fuzzy)
        if criteria.get('Manufacturer'):
            manufacturer_criteria = criteria['Manufacturer'].lower()
            manufacturer_extracted = extracted.get('manufacturer', '').lower()

            if manufacturer_criteria not in manufacturer_extracted and \
               manufacturer_extracted not in manufacturer_criteria:
                return False

        # Model must match (case-insensitive, fuzzy)
        if criteria.get('Model'):
            model_criteria = criteria['Model'].lower()
            model_extracted = extracted.get('model', '').lower()

            if model_criteria not in model_extracted and \
               model_extracted not in model_criteria:
                return False

        # Reference number if specified (exact match)
        if criteria.get('Reference_Number'):
            ref_criteria = criteria['Reference_Number'].replace('-', '').replace(' ', '').lower()
            ref_extracted = extracted.get('reference_number', '').replace('-', '').replace(' ', '').lower()

            if ref_criteria and ref_extracted and ref_criteria != ref_extracted:
                return False

        # Year if specified (exact match or within 1 year)
        if criteria.get('Year') and extracted.get('year'):
            if abs(criteria['Year'] - extracted['year']) > 1:
                return False

        return True

    def filter_by_country(
        self,
        extracted: Dict[str, Any],
        allowed_countries: List[str]
    ) -> bool:
        """
        Strict country filtering

        Args:
            extracted: Extracted watch data
            allowed_countries: List of allowed countries

        Returns:
            True if country is allowed or unknown, False otherwise
        """
        if not allowed_countries:
            return True  # No filter applied

        country = extracted.get('country', '').strip()

        if not country:
            # If OpenAI couldn't extract country, allow it
            # (user can manually verify in Notion)
            logger.warning("Country not extracted - allowing listing")
            return True

        # Normalize country names
        country_normalized = country.lower()
        allowed_normalized = [c.lower() for c in allowed_countries]

        # Check if extracted country is in allowed list
        for allowed in allowed_normalized:
            if allowed in country_normalized or country_normalized in allowed:
                return True

        # Strict: reject if country not in allowed list
        logger.info(f"Filtered out listing from {country} (not in {allowed_countries})")
        return False

    def batch_extract(
        self,
        listings: List[Dict[str, str]],
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extract data from multiple listings

        Args:
            listings: List of raw listings with 'raw_html' key
            source_name: Source website name

        Returns:
            List of successfully extracted watch data
        """
        results = []

        for i, listing in enumerate(listings):
            logger.info(f"Extracting {i+1}/{len(listings)} from {source_name}")

            extracted = self.extract_watch_data(
                listing.get('raw_html', ''),
                source_name
            )

            if extracted:
                # Merge with original listing data
                extracted.update({
                    'link': listing.get('link'),
                    'source_name': source_name,
                    'source_type': listing.get('source_type')
                })
                results.append(extracted)

        logger.info(f"Successfully extracted {len(results)}/{len(listings)} listings")
        return results
