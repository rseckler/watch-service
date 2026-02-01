"""
Supabase Client - Database operations for Watch Service
Handles all interactions with Supabase PostgreSQL database
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Wrapper for Supabase database operations
    Manages watch sources, search criteria, listings, and sync history
    """

    def __init__(self):
        """Initialize Supabase client with credentials from .env"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.url or not self.key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")

        self.client: Client = create_client(self.url, self.key)
        logger.info("✅ Supabase client initialized")

    # ========================================
    # SOURCES
    # ========================================

    def get_active_sources(self) -> List[Dict]:
        """
        Get all active sources from watch_sources table
        Returns list of source configurations with CSS selectors
        """
        try:
            response = self.client.table('watch_sources').select('*').eq('active', True).execute()
            sources = response.data
            logger.info(f"📋 Loaded {len(sources)} active sources")
            return sources
        except Exception as e:
            logger.error(f"❌ Error loading sources: {e}")
            return []

    def update_source_stats(self, source_id: str, success: bool, error_msg: Optional[str] = None):
        """
        Update source statistics after scraping attempt

        Args:
            source_id: UUID of the source
            success: Whether scraping was successful
            error_msg: Error message if failed
        """
        try:
            if success:
                # Reset error count, update last successful scrape
                self.client.table('watch_sources').update({
                    'last_successful_scrape': datetime.now().isoformat(),
                    'error_count': 0,
                    'updated_at': datetime.now().isoformat()
                }).eq('id', source_id).execute()
                logger.debug(f"✅ Updated stats for source {source_id}")
            else:
                # Increment error count
                response = self.client.table('watch_sources').select('error_count').eq('id', source_id).execute()
                if response.data:
                    current_errors = response.data[0].get('error_count', 0)
                    self.client.table('watch_sources').update({
                        'error_count': current_errors + 1,
                        'updated_at': datetime.now().isoformat()
                    }).eq('id', source_id).execute()
                    logger.warning(f"⚠️ Error count increased for source {source_id}: {error_msg}")
        except Exception as e:
            logger.error(f"❌ Error updating source stats: {e}")

    # ========================================
    # SEARCH CRITERIA
    # ========================================

    def get_search_criteria(self) -> List[Dict]:
        """
        Get all active search criteria
        Returns list of watch models to search for
        """
        try:
            response = self.client.table('watch_search_criteria').select('*').eq('active', True).execute()
            criteria = response.data
            logger.info(f"🔍 Loaded {len(criteria)} active search criteria")
            return criteria
        except Exception as e:
            logger.error(f"❌ Error loading search criteria: {e}")
            return []

    # ========================================
    # LISTINGS
    # ========================================

    def get_existing_url_hashes(self) -> List[str]:
        """
        Get all existing URL hashes for duplicate detection
        Returns list of url_hash strings
        """
        try:
            response = self.client.table('watch_listings').select('url_hash').execute()
            hashes = [item['url_hash'] for item in response.data]
            logger.debug(f"📊 Loaded {len(hashes)} existing URL hashes")
            return hashes
        except Exception as e:
            logger.error(f"❌ Error loading URL hashes: {e}")
            return []

    def create_listing(self, data: Dict) -> Optional[str]:
        """
        Create new watch listing

        Args:
            data: Dictionary with listing properties

        Returns:
            UUID of created listing or None if failed
        """
        try:
            # Ensure required fields
            listing_data = {
                'name': data.get('name', 'Unknown Watch'),
                'date_found': datetime.now().isoformat(),
                'manufacturer': data.get('manufacturer'),
                'model': data.get('model'),
                'reference_number': data.get('reference_number'),
                'year': data.get('year'),
                'condition': data.get('condition', 'Unbekannt'),
                'price': data.get('price'),
                'currency': data.get('currency', 'EUR'),
                'location': data.get('location'),
                'country': data.get('country'),
                'link': data['link'],  # Required
                'seller_name': data.get('seller_name'),
                'seller_url': data.get('seller_url'),
                'source': data['source'],  # Required
                'source_type': data.get('source_type'),
                'availability': 'Available',
                'last_checked': datetime.now().isoformat(),
                'url_hash': data['url_hash'],  # Required
                'search_criteria_id': data.get('search_criteria_id'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            response = self.client.table('watch_listings').insert(listing_data).execute()
            listing_id = response.data[0]['id']
            logger.info(f"✅ Created listing: {data.get('name')} from {data['source']}")
            return listing_id
        except Exception as e:
            logger.error(f"❌ Error creating listing: {e}")
            return None

    def get_available_listings(self) -> List[Dict]:
        """
        Get all listings marked as Available
        Used for availability checking
        """
        try:
            response = self.client.table('watch_listings').select('*').eq('availability', 'Available').execute()
            listings = response.data
            logger.info(f"📋 Loaded {len(listings)} available listings")
            return listings
        except Exception as e:
            logger.error(f"❌ Error loading available listings: {e}")
            return []

    def update_availability(self, listing_id: str, status: str, sold_at: Optional[datetime] = None):
        """
        Update listing availability status

        Args:
            listing_id: UUID of the listing
            status: 'Available', 'Sold', or 'Unknown'
            sold_at: Timestamp when marked as sold
        """
        try:
            update_data = {
                'availability': status,
                'last_checked': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            if status == 'Sold' and sold_at:
                update_data['sold_at'] = sold_at.isoformat()

            self.client.table('watch_listings').update(update_data).eq('id', listing_id).execute()
            logger.info(f"✅ Updated availability for listing {listing_id}: {status}")
        except Exception as e:
            logger.error(f"❌ Error updating availability: {e}")

    # ========================================
    # SYNC HISTORY
    # ========================================

    def log_search_run(self, stats: Dict):
        """
        Log search run statistics to sync_history

        Args:
            stats: Dictionary with run statistics
        """
        try:
            log_data = {
                'name': f"Search Run {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'date': datetime.now().isoformat(),
                'status': stats.get('status', 'Success'),
                'sources_checked': stats.get('sources_checked', 0),
                'sources_failed': stats.get('sources_failed', 0),
                'listings_found': stats.get('listings_found', 0),
                'listings_saved': stats.get('listings_saved', 0),
                'duplicates_skipped': stats.get('duplicates_skipped', 0),
                'duration_seconds': stats.get('duration_seconds', 0),
                'error_message': stats.get('error_message'),
                'created_at': datetime.now().isoformat()
            }

            self.client.table('watch_sync_history').insert(log_data).execute()
            logger.info(f"📊 Logged search run: {stats.get('listings_found', 0)} found, {stats.get('listings_saved', 0)} saved")
        except Exception as e:
            logger.error(f"❌ Error logging search run: {e}")

    # ========================================
    # UTILITY METHODS
    # ========================================

    def test_connection(self) -> bool:
        """
        Test database connection
        Returns True if connection works
        """
        try:
            response = self.client.table('watch_sources').select('id').limit(1).execute()
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def get_stats(self) -> Dict:
        """
        Get overall database statistics
        """
        try:
            sources_count = len(self.client.table('watch_sources').select('id').execute().data)
            criteria_count = len(self.client.table('watch_search_criteria').select('id').execute().data)
            listings_count = len(self.client.table('watch_listings').select('id').execute().data)
            available_count = len(self.client.table('watch_listings').select('id').eq('availability', 'Available').execute().data)

            stats = {
                'sources': sources_count,
                'search_criteria': criteria_count,
                'total_listings': listings_count,
                'available_listings': available_count
            }

            logger.info(f"📊 Database stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}


if __name__ == '__main__':
    # Test connection
    logging.basicConfig(level=logging.INFO)
    client = SupabaseClient()

    print("\n" + "=" * 70)
    print("🧪 Testing Supabase Client")
    print("=" * 70 + "\n")

    # Test connection
    if client.test_connection():
        print("✅ Connection test passed\n")
    else:
        print("❌ Connection test failed\n")
        exit(1)

    # Get stats
    stats = client.get_stats()
    print("📊 Database Statistics:")
    print(f"   Sources: {stats.get('sources', 0)}")
    print(f"   Search Criteria: {stats.get('search_criteria', 0)}")
    print(f"   Total Listings: {stats.get('total_listings', 0)}")
    print(f"   Available Listings: {stats.get('available_listings', 0)}")
    print()

    # Test loading sources
    sources = client.get_active_sources()
    print(f"✅ Loaded {len(sources)} active sources:")
    for source in sources[:3]:
        print(f"   - {source['name']} ({source['type']})")
    if len(sources) > 3:
        print(f"   ... and {len(sources) - 3} more")
    print()

    print("=" * 70)
    print("🎉 All tests passed!")
    print("=" * 70)
