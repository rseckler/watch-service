"""
Main search script - orchestrates watch searching across all sources
Runs hourly via cronjob
"""
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.supabase_client import SupabaseClient
from core.openai_extractor import OpenAIExtractor
from core.email_sender import EmailSender
from scrapers import CustomScraperLoader
from utils import setup_logger, generate_url_hash

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger('watch_searcher', 'watch_service.log')


class WatchSearcher:
    """Main orchestrator for watch searching"""

    def __init__(self):
        """Initialize all services"""
        self.db = SupabaseClient()
        self.openai = OpenAIExtractor()
        self.email = EmailSender()

        self.stats = {
            'sources_checked': 0,
            'sources_failed': 0,
            'listings_found': 0,
            'listings_saved': 0,
            'duplicates_skipped': 0,
            'duration_seconds': 0,
            'status': 'Success'
        }

        self.new_listings = []
        self.start_time = None

    def run(self):
        """Main execution flow"""
        try:
            self.start_time = datetime.now()
            logger.info("=" * 60)
            logger.info("🚀 Watch Service - Starting Search")
            logger.info("=" * 60)

            # Load configuration from Supabase
            sources = self.db.get_active_sources()
            criteria_list = self.db.get_search_criteria()
            existing_hashes = self.db.get_existing_url_hashes()

            if not sources:
                logger.warning("No active sources configured in database")
                return

            if not criteria_list:
                logger.warning("No active search criteria configured in database")
                return

            logger.info(f"📋 Loaded {len(sources)} sources and {len(criteria_list)} search criteria")

            # Search all sources for all criteria
            for source_config in sources:
                self._search_source(source_config, criteria_list, existing_hashes)

            # Send email notification if new listings found
            if self.new_listings:
                logger.info(f"📧 Sending email with {len(self.new_listings)} new listings")
                self.email.send_new_watches_email(self.new_listings)

            # Calculate duration
            duration = (datetime.now() - self.start_time).total_seconds()
            self.stats['duration_seconds'] = int(duration)

            # Log summary
            self._log_summary()

            # Log to database
            self.db.log_search_run(self.stats)

            logger.info("=" * 60)
            logger.info("✅ Search completed successfully")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"💥 Fatal error: {e}", exc_info=True)
            self.stats['status'] = 'Failed'
            self.stats['error_message'] = str(e)
            self.db.log_search_run(self.stats)
            self.email.send_error_notification(str(e))
            raise

    def _search_source(
        self,
        source_config: Dict[str, Any],
        criteria_list: List[Dict[str, Any]],
        existing_hashes: set
    ):
        """
        Search single source for all criteria

        Args:
            source_config: Source configuration from Notion
            criteria_list: List of search criteria
            existing_hashes: Set of existing URL hashes
        """
        source_name = source_config.get('name', 'Unknown')
        source_id = source_config.get('id')

        try:
            logger.info(f"\n🌐 Searching {source_name}...")
            self.stats['sources_checked'] += 1

            # Load appropriate scraper (generic or custom)
            scraper = CustomScraperLoader.load_scraper(source_config)

            # Search for each criteria
            all_findings = []

            for criteria in criteria_list:
                manufacturer = criteria.get('manufacturer', '')
                model = criteria.get('model', '')

                logger.info(f"  🔍 {manufacturer} {model}")

                try:
                    findings = scraper.search(criteria)
                    all_findings.extend([
                        {**f, 'criteria': criteria} for f in findings
                    ])
                except Exception as e:
                    logger.error(f"  ❌ Search failed: {e}")
                    continue

            if not all_findings:
                logger.info(f"  ℹ️  No listings found")
                scraper.close_driver()
                self.db.update_source_stats(source_id, success=True)
                return

            logger.info(f"  ✅ Found {len(all_findings)} raw listings")

            # Extract structured data with OpenAI
            extracted = self._extract_and_filter(all_findings, existing_hashes)

            # Save to database
            saved_count = self._save_listings(extracted)

            logger.info(f"  💾 Saved {saved_count} new listings")

            # Close scraper
            scraper.close_driver()

            # Update source stats
            self.db.update_source_stats(source_id, success=True)

        except Exception as e:
            logger.error(f"  ❌ {source_name} failed: {e}")
            self.stats['sources_failed'] += 1
            self.db.update_source_stats(source_id, success=False, error_msg=str(e))

    def _extract_and_filter(
        self,
        findings: List[Dict[str, Any]],
        existing_hashes: set
    ) -> List[Dict[str, Any]]:
        """
        Extract structured data with OpenAI and filter

        Args:
            findings: Raw findings from scraper
            existing_hashes: Set of existing URL hashes

        Returns:
            List of validated, filtered listings
        """
        results = []

        for finding in findings:
            try:
                # Extract structured data
                extracted = self.openai.extract_watch_data(
                    finding.get('raw_html', ''),
                    finding.get('source_name', '')
                )

                if not extracted:
                    continue

                # Check if matches criteria
                criteria = finding.get('criteria', {})
                if not self.openai.match_search_criteria(extracted, criteria):
                    logger.debug("  ⊘ Doesn't match criteria")
                    continue

                # Filter by country
                allowed_countries = criteria.get('allowed_countries', [])
                if not self.openai.filter_by_country(extracted, allowed_countries):
                    logger.debug("  ⊘ Filtered by country")
                    continue

                # Check duplicates
                url = finding.get('link', '')
                url_hash = generate_url_hash(url)

                if url_hash in existing_hashes:
                    self.stats['duplicates_skipped'] += 1
                    logger.debug("  ⊘ Duplicate (already in DB)")
                    continue

                # Merge extracted data with original finding
                listing = {
                    **extracted,
                    'link': url,
                    'url_hash': url_hash,
                    'criteria_id': criteria.get('id'),
                    'source_name': finding.get('source_name'),
                    'source_type': finding.get('source_type')
                }

                results.append(listing)
                self.stats['listings_found'] += 1

            except Exception as e:
                logger.error(f"  ❌ Extraction failed: {e}")
                continue

        return results

    def _save_listings(self, listings: List[Dict[str, Any]]) -> int:
        """
        Save listings to database

        Args:
            listings: Extracted listings

        Returns:
            Number of listings saved
        """
        saved = 0

        for listing in listings:
            try:
                # Build listing data for Supabase
                listing_data = {
                    'name': f"{listing.get('manufacturer', 'Unknown')} {listing.get('model', '')}",
                    'manufacturer': listing.get('manufacturer', ''),
                    'model': listing.get('model', ''),
                    'reference_number': listing.get('reference_number', ''),
                    'year': listing.get('year'),
                    'condition': listing.get('condition', 'Unbekannt'),
                    'price': listing.get('price'),
                    'currency': listing.get('currency', 'EUR'),
                    'location': listing.get('location', ''),
                    'country': listing.get('country', ''),
                    'link': listing.get('link', ''),
                    'seller_name': listing.get('seller_name', ''),
                    'seller_url': listing.get('seller_url', ''),
                    'source': listing.get('source_name', 'Unknown'),
                    'source_type': listing.get('source_type', 'Unknown'),
                    'url_hash': listing.get('url_hash', ''),
                    'search_criteria_id': listing.get('criteria_id'),
                }

                # Create in Supabase
                self.db.create_listing(listing_data)

                # Track for email
                self.new_listings.append(listing_data)

                saved += 1
                self.stats['listings_saved'] += 1

            except Exception as e:
                logger.error(f"  ❌ Failed to save listing: {e}")
                continue

        return saved

    def _log_summary(self):
        """Log execution summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Sources checked:     {self.stats['sources_checked']}")
        logger.info(f"Sources failed:      {self.stats['sources_failed']}")
        logger.info(f"Listings found:      {self.stats['listings_found']}")
        logger.info(f"Listings saved:      {self.stats['listings_saved']}")
        logger.info(f"Duplicates skipped:  {self.stats['duplicates_skipped']}")
        logger.info(f"Duration:            {self.stats['duration_seconds']}s")
        logger.info(f"Status:              {self.stats['status']}")
        logger.info("=" * 60)


def main():
    """Entry point"""
    try:
        searcher = WatchSearcher()
        searcher.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
