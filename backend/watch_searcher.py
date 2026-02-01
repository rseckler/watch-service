#!/usr/bin/env python3
"""
Watch Searcher - Main Script
Orchestrates the watch scraping process across all sources
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.openai_extractor import OpenAIExtractor
from scrapers.cologne_watch_scraper import CologneWatchScraper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watch_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WatchSearcher:
    """Main orchestrator for watch scraping"""

    def __init__(self):
        """Initialize searcher with database and OpenAI"""
        logger.info("=" * 60)
        logger.info("🔍 Watch Searcher Starting...")
        logger.info("=" * 60)

        try:
            self.db = Database()
            self.extractor = OpenAIExtractor()
            self.scrapers = self._initialize_scrapers()

            # Statistics
            self.stats = {
                'sources_checked': 0,
                'sources_failed': 0,
                'listings_found': 0,
                'listings_saved': 0,
                'duplicates_skipped': 0,
                'start_time': time.time()
            }

            logger.info(f"✓ Initialized {len(self.scrapers)} scrapers")

        except Exception as e:
            logger.error(f"✗ Initialization failed: {e}")
            raise

    def _initialize_scrapers(self) -> list:
        """Initialize all available scrapers"""
        # Start with just one scraper for testing
        scrapers = [
            CologneWatchScraper(),
        ]

        # TODO: Add more scrapers as they're implemented
        # scrapers.append(WatchViceScraper())
        # scrapers.append(WatchDeScraper())
        # etc.

        return scrapers

    def run(self):
        """Main execution: search all sources and save results"""
        try:
            # Get active search criteria
            criteria_list = self.db.get_active_search_criteria()

            if not criteria_list:
                logger.warning("⚠ No active search criteria found")
                self._log_search_run("Success", error_message="No active search criteria")
                return

            logger.info(f"📋 Found {len(criteria_list)} active search criteria")

            # Get existing URL hashes for duplicate detection
            existing_hashes = self.db.get_existing_url_hashes()
            logger.info(f"📊 {len(existing_hashes)} existing listings in database")

            # Process each search criteria
            for criteria in criteria_list:
                logger.info("")
                logger.info(f"🎯 Searching for: {criteria['manufacturer']} {criteria['model']}")

                # Search each source
                for scraper in self.scrapers:
                    self._search_source(scraper, criteria, existing_hashes)

            # Log the search run
            self._log_search_run("Success")

            # Print summary
            self._print_summary()

        except Exception as e:
            logger.error(f"✗ Search run failed: {e}")
            self._log_search_run("Failed", error_message=str(e))
            raise

        finally:
            # Cleanup
            for scraper in self.scrapers:
                scraper.close()
            self.db.close()

    def _search_source(self, scraper, criteria: dict, existing_hashes: set):
        """Search a single source for watches"""
        try:
            self.stats['sources_checked'] += 1

            # Search the source
            raw_listings = scraper.search(criteria)
            self.stats['listings_found'] += len(raw_listings)

            if not raw_listings:
                return

            # Process each listing
            for raw_listing in raw_listings:
                # Check for duplicates
                if raw_listing['url_hash'] in existing_hashes:
                    self.stats['duplicates_skipped'] += 1
                    logger.debug(f"  ⊗ Duplicate: {raw_listing['title']}")
                    continue

                # Extract structured data with OpenAI
                extracted = self.extractor.extract_watch_data(
                    raw_text=raw_listing['raw_html'],
                    source_name=scraper.source_name,
                    search_criteria=criteria
                )

                if not extracted:
                    logger.warning(f"  ⚠ Could not extract data from: {raw_listing['title']}")
                    continue

                # Check if matches search criteria
                if not self.extractor.match_search_criteria(extracted, criteria):
                    logger.debug(f"  ⊗ Does not match criteria: {extracted['manufacturer']} {extracted['model']}")
                    continue

                # Check country filter
                allowed_countries = criteria.get('allowed_countries')
                if allowed_countries and not self.extractor.filter_by_country(extracted, allowed_countries):
                    continue

                # Save to database
                if self._save_listing(extracted, raw_listing, criteria):
                    self.stats['listings_saved'] += 1
                    existing_hashes.add(raw_listing['url_hash'])

        except Exception as e:
            logger.error(f"✗ Source {scraper.source_name} failed: {e}")
            self.stats['sources_failed'] += 1

    def _save_listing(self, extracted: dict, raw_listing: dict, criteria: dict) -> bool:
        """Save a listing to the database"""
        try:
            listing_data = {
                'name': f"{extracted['manufacturer']} {extracted['model']}",
                'manufacturer': extracted['manufacturer'],
                'model': extracted['model'],
                'reference_number': extracted.get('reference_number'),
                'year': extracted.get('year'),
                'condition': extracted.get('condition'),
                'price': extracted.get('price'),
                'currency': extracted.get('currency'),
                'location': extracted.get('location'),
                'country': extracted.get('country'),
                'link': raw_listing['link'],
                'seller_name': extracted.get('seller_name') or raw_listing['source_name'],
                'seller_url': raw_listing.get('source_url', ''),
                'source': raw_listing['source_name'],
                'source_type': raw_listing['source_type'],
                'availability': 'Available',
                'url_hash': raw_listing['url_hash'],
                'search_criteria_id': criteria['id'],
                'image_url': raw_listing.get('image_url') or criteria.get('image_url')
            }

            listing_id = self.db.create_listing(listing_data)
            return listing_id is not None

        except Exception as e:
            logger.error(f"Failed to save listing: {e}")
            return False

    def _log_search_run(self, status: str, error_message: str = None):
        """Log the search run to sync history"""
        duration = int(time.time() - self.stats['start_time'])

        log_data = {
            'name': f"Automatischer Suchlauf {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'status': status,
            'sources_checked': self.stats['sources_checked'],
            'sources_failed': self.stats['sources_failed'],
            'listings_found': self.stats['listings_found'],
            'listings_saved': self.stats['listings_saved'],
            'duplicates_skipped': self.stats['duplicates_skipped'],
            'duration_seconds': duration,
            'error_message': error_message
        }

        self.db.create_sync_log(log_data)

    def _print_summary(self):
        """Print execution summary"""
        duration = int(time.time() - self.stats['start_time'])

        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 SEARCH SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Sources checked:     {self.stats['sources_checked']}")
        logger.info(f"Sources failed:      {self.stats['sources_failed']}")
        logger.info(f"Listings found:      {self.stats['listings_found']}")
        logger.info(f"Listings saved:      {self.stats['listings_saved']}")
        logger.info(f"Duplicates skipped:  {self.stats['duplicates_skipped']}")
        logger.info(f"Duration:            {duration}s")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    try:
        searcher = WatchSearcher()
        searcher.run()
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
