"""
Notion API client for Watch Service
Handles all interactions with Notion databases
"""
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from notion_client import Client
from utils.logger import get_logger

logger = get_logger(__name__)


class NotionWatchClient:
    """Notion API wrapper for Watch Service"""

    def __init__(self):
        """Initialize Notion client with credentials from environment"""
        self.client = Client(auth=os.getenv('NOTION_API_KEY'))
        self.sources_db_id = os.getenv('SOURCES_DB_ID')
        self.search_criteria_db_id = os.getenv('SEARCH_CRITERIA_DB_ID')
        self.listings_db_id = os.getenv('LISTINGS_DB_ID')
        self.sync_history_db_id = os.getenv('SYNC_HISTORY_DB_ID')

        # Validate configuration
        if not all([
            self.sources_db_id,
            self.search_criteria_db_id,
            self.listings_db_id,
            self.sync_history_db_id
        ]):
            raise ValueError("Missing Notion database IDs in .env file")

    def get_active_sources(self) -> List[Dict[str, Any]]:
        """
        Load active sources from Sources database

        Returns:
            List of source configurations with Active=True
        """
        try:
            results = []
            has_more = True
            start_cursor = None

            while has_more:
                response = self.client.databases.query(
                    database_id=self.sources_db_id,
                    filter={
                        "property": "Active",
                        "checkbox": {
                            "equals": True
                        }
                    },
                    start_cursor=start_cursor
                )

                for page in response['results']:
                    props = page['properties']
                    source = {
                        'id': page['id'],
                        'Name': self._get_title(props.get('Name')),
                        'URL': self._get_url(props.get('URL')),
                        'Domain': self._get_rich_text(props.get('Domain')),
                        'Type': self._get_select(props.get('Type')),
                        'Scraper_Type': self._get_select(props.get('Scraper_Type')),
                        'Requires_Auth': self._get_checkbox(props.get('Requires_Auth')),
                        'Rate_Limit_Seconds': self._get_number(props.get('Rate_Limit_Seconds')) or 2,
                        'Search_URL_Template': self._get_rich_text(props.get('Search_URL_Template')),
                        'Listing_Selector': self._get_rich_text(props.get('Listing_Selector')),
                        'Title_Selector': self._get_rich_text(props.get('Title_Selector')),
                        'Price_Selector': self._get_rich_text(props.get('Price_Selector')),
                        'Link_Selector': self._get_rich_text(props.get('Link_Selector')),
                        'Image_Selector': self._get_rich_text(props.get('Image_Selector')),
                        'Custom_Scraper': self._get_rich_text(props.get('Custom_Scraper')),
                        'Auth_Username_Env': self._get_rich_text(props.get('Auth_Username_Env')),
                        'Auth_Password_Env': self._get_rich_text(props.get('Auth_Password_Env')),
                    }
                    results.append(source)

                has_more = response['has_more']
                start_cursor = response.get('next_cursor')

            logger.info(f"Loaded {len(results)} active sources from Notion")
            return results

        except Exception as e:
            logger.error(f"Failed to load sources: {e}")
            raise

    def get_search_criteria(self) -> List[Dict[str, Any]]:
        """
        Load active search criteria from Watch_Search_Criteria database

        Returns:
            List of active search criteria
        """
        try:
            results = []
            has_more = True
            start_cursor = None

            while has_more:
                response = self.client.databases.query(
                    database_id=self.search_criteria_db_id,
                    filter={
                        "property": "Active",
                        "checkbox": {
                            "equals": True
                        }
                    },
                    start_cursor=start_cursor
                )

                for page in response['results']:
                    props = page['properties']
                    criteria = {
                        'id': page['id'],
                        'Manufacturer': self._get_rich_text(props.get('Manufacturer')),
                        'Model': self._get_rich_text(props.get('Model')),
                        'Reference_Number': self._get_rich_text(props.get('Reference_Number')),
                        'Year': self._get_number(props.get('Year')),
                        'Allowed_Countries': self._get_multi_select(props.get('Allowed_Countries')),
                    }
                    results.append(criteria)

                has_more = response['has_more']
                start_cursor = response.get('next_cursor')

            logger.info(f"Loaded {len(results)} active search criteria from Notion")
            return results

        except Exception as e:
            logger.error(f"Failed to load search criteria: {e}")
            raise

    def get_existing_url_hashes(self) -> set:
        """
        Fetch all existing URL hashes for duplicate detection

        Returns:
            Set of URL hashes
        """
        try:
            hashes = set()
            has_more = True
            start_cursor = None

            while has_more:
                response = self.client.databases.query(
                    database_id=self.listings_db_id,
                    start_cursor=start_cursor
                )

                for page in response['results']:
                    url_hash = self._get_rich_text(page['properties'].get('URL_Hash'))
                    if url_hash:
                        hashes.add(url_hash)

                has_more = response['has_more']
                start_cursor = response.get('next_cursor')

            logger.info(f"Loaded {len(hashes)} existing URL hashes")
            return hashes

        except Exception as e:
            logger.error(f"Failed to load URL hashes: {e}")
            raise

    def create_listing(self, data: Dict[str, Any]) -> str:
        """
        Create new listing in Watch_Listings database

        Args:
            data: Listing data with keys matching Notion properties

        Returns:
            Created page ID
        """
        try:
            properties = {
                "Name": {"title": [{"text": {"content": data.get('Name', 'Untitled')}}]},
                "Date_Found": {"date": {"start": datetime.now().isoformat()}},
                "Manufacturer": {"rich_text": [{"text": {"content": data.get('Manufacturer', '')}}]},
                "Model": {"rich_text": [{"text": {"content": data.get('Model', '')}}]},
                "Reference_Number": {"rich_text": [{"text": {"content": data.get('Reference_Number', '')}}]},
                "Price": {"number": data.get('Price')},
                "Currency": {"select": {"name": data.get('Currency', 'EUR')}},
                "Location": {"rich_text": [{"text": {"content": data.get('Location', '')}}]},
                "Country": {"rich_text": [{"text": {"content": data.get('Country', '')}}]},
                "Link": {"url": data.get('Link', '')},
                "Seller_Name": {"rich_text": [{"text": {"content": data.get('Seller_Name', '')}}]},
                "Source": {"select": {"name": data.get('Source', 'Unknown')}},
                "Source_Type": {"select": {"name": data.get('Source_Type', 'Unknown')}},
                "Availability": {"select": {"name": "Available"}},
                "URL_Hash": {"rich_text": [{"text": {"content": data.get('URL_Hash', '')}}]},
            }

            # Optional fields
            if data.get('Year'):
                properties["Year"] = {"number": data['Year']}
            if data.get('Condition'):
                properties["Condition"] = {"select": {"name": data['Condition']}}
            if data.get('Seller_URL'):
                properties["Seller_URL"] = {"url": data['Seller_URL']}
            if data.get('Search_Criteria_ID'):
                properties["Search_Criteria_ID"] = {"relation": [{"id": data['Search_Criteria_ID']}]}

            response = self.client.pages.create(
                parent={"database_id": self.listings_db_id},
                properties=properties
            )

            logger.info(f"Created listing: {data.get('Name')}")
            return response['id']

        except Exception as e:
            logger.error(f"Failed to create listing: {e}")
            raise

    def update_availability(self, page_id: str, status: str, sold_at: datetime = None):
        """
        Update listing availability status

        Args:
            page_id: Notion page ID
            status: 'Available', 'Sold', or 'Unknown'
            sold_at: Optional timestamp when marked sold
        """
        try:
            properties = {
                "Availability": {"select": {"name": status}},
                "Last_Checked": {"date": {"start": datetime.now().isoformat()}}
            }

            if sold_at:
                properties["Sold_At"] = {"date": {"start": sold_at.isoformat()}}

            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Updated availability: {page_id} -> {status}")

        except Exception as e:
            logger.error(f"Failed to update availability: {e}")
            raise

    def update_source_stats(self, source_id: str, success: bool, error_msg: str = None):
        """
        Update source statistics after scraping attempt

        Args:
            source_id: Notion source page ID
            success: Whether scrape was successful
            error_msg: Optional error message
        """
        try:
            properties = {}

            if success:
                properties["Last_Successful_Scrape"] = {"date": {"start": datetime.now().isoformat()}}
                properties["Error_Count"] = {"number": 0}
            else:
                # Increment error count
                page = self.client.pages.retrieve(page_id=source_id)
                current_errors = self._get_number(page['properties'].get('Error_Count')) or 0
                properties["Error_Count"] = {"number": current_errors + 1}

            if error_msg:
                properties["Notes"] = {"rich_text": [{"text": {"content": f"Error: {error_msg}"}}]}

            self.client.pages.update(page_id=source_id, properties=properties)

        except Exception as e:
            logger.error(f"Failed to update source stats: {e}")
            # Don't raise - this is non-critical

    def log_search_run(self, stats: Dict[str, Any]):
        """
        Log search run to Sync_History database

        Args:
            stats: Dictionary with run statistics
        """
        try:
            name = f"Search Run {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            properties = {
                "Name": {"title": [{"text": {"content": name}}]},
                "Date": {"date": {"start": datetime.now().isoformat()}},
                "Status": {"select": {"name": stats.get('status', 'Success')}},
                "Sources_Checked": {"number": stats.get('sources_checked', 0)},
                "Sources_Failed": {"number": stats.get('sources_failed', 0)},
                "Listings_Found": {"number": stats.get('listings_found', 0)},
                "Listings_Saved": {"number": stats.get('listings_saved', 0)},
                "Duplicates_Skipped": {"number": stats.get('duplicates_skipped', 0)},
                "Duration_Seconds": {"number": stats.get('duration_seconds', 0)},
            }

            if stats.get('error_message'):
                properties["Error_Message"] = {
                    "rich_text": [{"text": {"content": stats['error_message']}}]
                }

            self.client.pages.create(
                parent={"database_id": self.sync_history_db_id},
                properties=properties
            )

            logger.info(f"Logged search run: {name}")

        except Exception as e:
            logger.error(f"Failed to log search run: {e}")
            # Don't raise - logging failure shouldn't stop execution

    def get_available_listings(self) -> List[Dict[str, Any]]:
        """
        Get all listings with Availability='Available'

        Returns:
            List of available listings with id, Link, Last_Checked
        """
        try:
            results = []
            has_more = True
            start_cursor = None

            while has_more:
                response = self.client.databases.query(
                    database_id=self.listings_db_id,
                    filter={
                        "property": "Availability",
                        "select": {
                            "equals": "Available"
                        }
                    },
                    start_cursor=start_cursor
                )

                for page in response['results']:
                    props = page['properties']
                    listing = {
                        'id': page['id'],
                        'Link': self._get_url(props.get('Link')),
                        'Last_Checked': self._get_date(props.get('Last_Checked')),
                        'Source': self._get_select(props.get('Source')),
                    }
                    results.append(listing)

                has_more = response['has_more']
                start_cursor = response.get('next_cursor')

            logger.info(f"Loaded {len(results)} available listings")
            return results

        except Exception as e:
            logger.error(f"Failed to load available listings: {e}")
            raise

    # Helper methods for extracting Notion property values
    def _get_title(self, prop) -> str:
        if not prop or not prop.get('title'):
            return ""
        return prop['title'][0]['text']['content'] if prop['title'] else ""

    def _get_rich_text(self, prop) -> str:
        if not prop or not prop.get('rich_text'):
            return ""
        return prop['rich_text'][0]['text']['content'] if prop['rich_text'] else ""

    def _get_url(self, prop) -> str:
        if not prop:
            return ""
        return prop.get('url', '')

    def _get_number(self, prop) -> Optional[float]:
        if not prop:
            return None
        return prop.get('number')

    def _get_select(self, prop) -> str:
        if not prop or not prop.get('select'):
            return ""
        return prop['select']['name'] if prop['select'] else ""

    def _get_multi_select(self, prop) -> List[str]:
        if not prop or not prop.get('multi_select'):
            return []
        return [item['name'] for item in prop['multi_select']]

    def _get_checkbox(self, prop) -> bool:
        if not prop:
            return False
        return prop.get('checkbox', False)

    def _get_date(self, prop) -> Optional[str]:
        if not prop or not prop.get('date'):
            return None
        return prop['date']['start'] if prop['date'] else None
