"""
Database Connection Module
Handles all PostgreSQL database operations for the Watch Service
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection and operations"""

    def __init__(self):
        """Initialize database connection using environment variables"""
        # Use non-pooling URL for direct connection
        self.connection_string = os.getenv('POSTGRES_URL_NON_POOLING') or os.getenv('POSTGRES_URL')

        if not self.connection_string:
            raise ValueError("Database connection string not found in environment variables")

        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("✓ Database connected successfully")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Update execution failed: {e}")
            raise

    # ==================== WATCH SEARCH CRITERIA ====================

    def get_active_search_criteria(self) -> List[Dict]:
        """Get all active search criteria"""
        query = """
            SELECT * FROM watch_search_criteria
            WHERE active = true
            ORDER BY created_at DESC
        """
        return self.execute_query(query)

    # ==================== WATCH LISTINGS ====================

    def get_existing_url_hashes(self) -> set:
        """Get all existing URL hashes for duplicate detection"""
        query = "SELECT url_hash FROM watch_listings"
        results = self.execute_query(query)
        return {row['url_hash'] for row in results}

    def create_listing(self, listing_data: Dict) -> Optional[str]:
        """Create a new watch listing and return its ID"""
        query = """
            INSERT INTO watch_listings (
                name, manufacturer, model, reference_number, year, condition,
                price, currency, location, country, link, seller_name, seller_url,
                source, source_type, availability, url_hash, search_criteria_id,
                image_url, date_found, last_checked
            ) VALUES (
                %(name)s, %(manufacturer)s, %(model)s, %(reference_number)s, %(year)s, %(condition)s,
                %(price)s, %(currency)s, %(location)s, %(country)s, %(link)s, %(seller_name)s, %(seller_url)s,
                %(source)s, %(source_type)s, %(availability)s, %(url_hash)s, %(search_criteria_id)s,
                %(image_url)s, NOW(), NOW()
            ) RETURNING id
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, listing_data)
                self.conn.commit()
                listing_id = cursor.fetchone()[0]
                logger.info(f"✓ Created listing: {listing_data['name']}")
                return listing_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Failed to create listing: {e}")
            return None

    def get_available_listings(self) -> List[Dict]:
        """Get all listings that are marked as available"""
        query = """
            SELECT * FROM watch_listings
            WHERE availability = 'Available'
            ORDER BY date_found DESC
        """
        return self.execute_query(query)

    def mark_listing_sold(self, listing_id: str) -> bool:
        """Mark a listing as sold"""
        query = """
            UPDATE watch_listings
            SET availability = 'Sold', sold_at = NOW()
            WHERE id = %s
        """
        try:
            rows = self.execute_update(query, (listing_id,))
            return rows > 0
        except:
            return False

    def update_last_checked(self, listing_id: str) -> bool:
        """Update last_checked timestamp for a listing"""
        query = """
            UPDATE watch_listings
            SET last_checked = NOW()
            WHERE id = %s
        """
        try:
            rows = self.execute_update(query, (listing_id,))
            return rows > 0
        except:
            return False

    # ==================== SYNC HISTORY ====================

    def create_sync_log(self, log_data: Dict) -> Optional[str]:
        """Create a sync history log entry"""
        query = """
            INSERT INTO watch_sync_history (
                name, date, status, sources_checked, sources_failed,
                listings_found, listings_saved, duplicates_skipped,
                duration_seconds, error_message
            ) VALUES (
                %(name)s, NOW(), %(status)s, %(sources_checked)s, %(sources_failed)s,
                %(listings_found)s, %(listings_saved)s, %(duplicates_skipped)s,
                %(duration_seconds)s, %(error_message)s
            ) RETURNING id
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, log_data)
                self.conn.commit()
                log_id = cursor.fetchone()[0]
                logger.info(f"✓ Created sync log: {log_data['name']}")
                return log_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Failed to create sync log: {e}")
            return None
