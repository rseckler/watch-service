"""
Availability checker - marks listings as sold if no longer available
Runs hourly at :30 (offset from main search)
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.supabase_client import SupabaseClient
from scrapers import CustomScraperLoader
from utils import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger('availability_checker', 'availability_check.log')


class AvailabilityChecker:
    """Check if available listings are still active"""

    def __init__(self):
        """Initialize Supabase client"""
        self.db = SupabaseClient()
        self.stats = {
            'checked': 0,
            'still_available': 0,
            'marked_sold': 0,
            'errors': 0
        }

    def run(self):
        """Main execution flow"""
        try:
            logger.info("=" * 60)
            logger.info("🔍 Availability Checker - Starting")
            logger.info("=" * 60)

            # Get all available listings
            listings = self.db.get_available_listings()

            if not listings:
                logger.info("No available listings to check")
                return

            logger.info(f"Checking {len(listings)} available listings")

            # Load all active sources for scrapers
            sources = self.db.get_active_sources()
            source_map = {s['name']: s for s in sources}

            # Check each listing
            for listing in listings:
                self._check_listing(listing, source_map)

            # Log summary
            self._log_summary()

            logger.info("=" * 60)
            logger.info("✅ Availability check completed")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise

    def _check_listing(self, listing: dict, source_map: dict):
        """
        Check single listing availability

        Args:
            listing: Listing data from database
            source_map: Map of source name to config
        """
        listing_id = listing.get('id')
        url = listing.get('link')
        source_name = listing.get('source')

        if not url:
            logger.warning(f"Listing {listing_id} has no URL - skipping")
            return

        try:
            self.stats['checked'] += 1

            # Get source config
            source_config = source_map.get(source_name)
            if not source_config:
                logger.warning(f"Source {source_name} not found - skipping")
                return

            # Load scraper
            scraper = CustomScraperLoader.load_scraper(source_config)

            # Check availability
            is_available = scraper.check_availability(url)

            # Update Notion
            if not is_available:
                logger.info(f"❌ Marking as sold: {url}")
                self.db.update_availability(
                    listing_id,
                    status='Sold',
                    sold_at=datetime.now()
                )
                self.stats['marked_sold'] += 1
            else:
                logger.debug(f"✅ Still available: {url}")
                self.db.update_availability(
                    listing_id,
                    status='Available'
                )
                self.stats['still_available'] += 1

            # Close scraper
            scraper.close_driver()

        except Exception as e:
            logger.error(f"Failed to check {url}: {e}")
            self.stats['errors'] += 1

    def _log_summary(self):
        """Log execution summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Checked:          {self.stats['checked']}")
        logger.info(f"Still available:  {self.stats['still_available']}")
        logger.info(f"Marked sold:      {self.stats['marked_sold']}")
        logger.info(f"Errors:           {self.stats['errors']}")
        logger.info("=" * 60)


def main():
    """Entry point"""
    try:
        checker = AvailabilityChecker()
        checker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
