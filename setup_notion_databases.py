"""
One-time setup script to create Notion databases and populate Sources
Run once at project initialization
"""
import os
import sys
from getpass import getpass
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv()

# Notion database schemas and initial data

SOURCES_DATA = [
    # === DEALERS (9) ===
    {
        "Name": "Cologne Watch",
        "URL": "https://www.colognewatch.de",
        "Domain": "colognewatch.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://www.colognewatch.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".product-item",
        "Title_Selector": ".product-card__title",
        "Price_Selector": ".price-item",
        "Link_Selector": "a.product-item__link",
        "Notes": "German luxury watch dealer - Cologne"
    },
    {
        "Name": "Watch Vice",
        "URL": "https://watchvice.de",
        "Domain": "watchvice.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://watchvice.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".product",
        "Title_Selector": "h3.product-title",
        "Price_Selector": ".product-price",
        "Link_Selector": "a.product-link",
        "Notes": "Premium watch dealer based in Germany"
    },
    {
        "Name": "Watch.de",
        "URL": "https://www.watch.de",
        "Domain": "watch.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://www.watch.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".product-card",
        "Title_Selector": ".title",
        "Price_Selector": ".price",
        "Link_Selector": "a.link",
        "Notes": "German watch retailer"
    },
    {
        "Name": "Marks Uhren",
        "URL": "https://marks-uhren.de",
        "Domain": "marks-uhren.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://marks-uhren.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".product",
        "Title_Selector": ".name",
        "Price_Selector": ".price",
        "Link_Selector": "a",
        "Notes": "Watch dealer based in Germany"
    },
    {
        "Name": "Rothfuss Watches",
        "URL": "https://rothfuss-watches.de",
        "Domain": "rothfuss-watches.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://rothfuss-watches.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".item",
        "Title_Selector": ".title",
        "Price_Selector": ".price",
        "Link_Selector": "a",
        "Notes": "German watch specialist"
    },
    {
        "Name": "Karmann Watches",
        "URL": "https://karmannwatches.de",
        "Domain": "karmannwatches.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://karmannwatches.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".watch-item",
        "Title_Selector": ".watch-name",
        "Price_Selector": ".watch-price",
        "Link_Selector": "a",
        "Notes": "Watch dealer Germany"
    },
    {
        "Name": "Eupen Feine Uhren",
        "URL": "https://eupenfeineuhren.de",
        "Domain": "eupenfeineuhren.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://eupenfeineuhren.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".product",
        "Title_Selector": ".name",
        "Price_Selector": ".price",
        "Link_Selector": "a",
        "Notes": "Fine watch dealer"
    },
    {
        "Name": "G-Abriel",
        "URL": "https://www.g-abriel.de",
        "Domain": "g-abriel.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://www.g-abriel.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".watch",
        "Title_Selector": ".title",
        "Price_Selector": ".price",
        "Link_Selector": "a",
        "Notes": "Watch specialist Germany"
    },
    {
        "Name": "Bachmann & Scher",
        "URL": "https://www.bachmann-scher.de",
        "Domain": "bachmann-scher.de",
        "Type": "Dealer",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://www.bachmann-scher.de/gebrauchte-luxusuhren-kaufen.html?q={manufacturer}+{model}",
        "Listing_Selector": ".watch-item",
        "Title_Selector": ".title",
        "Price_Selector": ".price",
        "Link_Selector": "a",
        "Notes": "Used luxury watch dealer"
    },

    # === FORUMS (3) ===
    {
        "Name": "Uhrforum.de",
        "URL": "https://uhrforum.de/forums/angebote.11/",
        "Domain": "uhrforum.de",
        "Type": "Forum",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": True,
        "Rate_Limit_Seconds": 3,
        "Auth_Username_Env": "UHRFORUM_USERNAME",
        "Auth_Password_Env": "UHRFORUM_PASSWORD",
        "Search_URL_Template": "https://uhrforum.de/search/search?keywords={manufacturer}+{model}",
        "Listing_Selector": ".structItem",
        "Title_Selector": ".structItem-title",
        "Price_Selector": ".structItem-cell--meta",
        "Link_Selector": "a.structItem-title",
        "Notes": "Major German watch forum - requires login"
    },
    {
        "Name": "WatchLounge Forum",
        "URL": "https://forum.watchlounge.com",
        "Domain": "forum.watchlounge.com",
        "Type": "Forum",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": True,
        "Rate_Limit_Seconds": 3,
        "Auth_Username_Env": "WATCHLOUNGE_USERNAME",
        "Auth_Password_Env": "WATCHLOUNGE_PASSWORD",
        "Search_URL_Template": "https://forum.watchlounge.com/search?q={manufacturer}+{model}",
        "Listing_Selector": ".topic",
        "Title_Selector": ".topic-title",
        "Price_Selector": ".topic-meta",
        "Link_Selector": "a",
        "Notes": "Watch enthusiast forum"
    },
    {
        "Name": "Uhr-Forum.org",
        "URL": "https://uhr-forum.org/forum/",
        "Domain": "uhr-forum.org",
        "Type": "Forum",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": True,
        "Rate_Limit_Seconds": 3,
        "Auth_Username_Env": "UHR_FORUM_ORG_USERNAME",
        "Auth_Password_Env": "UHR_FORUM_ORG_PASSWORD",
        "Search_URL_Template": "https://uhr-forum.org/forum/search?q={manufacturer}+{model}",
        "Listing_Selector": ".post",
        "Title_Selector": ".post-title",
        "Price_Selector": ".post-meta",
        "Link_Selector": "a",
        "Notes": "German watch forum"
    },

    # === MARKETPLACES (5) ===
    {
        "Name": "eBay.de",
        "URL": "https://www.ebay.de",
        "Domain": "ebay.de",
        "Type": "Marketplace",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 3,
        "Search_URL_Template": "https://www.ebay.de/sch/i.html?_nkw={manufacturer}+{model}",
        "Listing_Selector": ".s-item",
        "Title_Selector": ".s-item__title",
        "Price_Selector": ".s-item__price",
        "Link_Selector": "a.s-item__link",
        "Notes": "eBay Germany - no login required for browsing"
    },
    {
        "Name": "Kleinanzeigen.de",
        "URL": "https://www.kleinanzeigen.de",
        "Domain": "kleinanzeigen.de",
        "Type": "Marketplace",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 3,
        "Search_URL_Template": "https://www.kleinanzeigen.de/s-uhren/c172?q={manufacturer}+{model}",
        "Listing_Selector": "article.aditem",
        "Title_Selector": ".text-module-begin",
        "Price_Selector": ".aditem-main--middle--price",
        "Link_Selector": "a.ellipsis",
        "Notes": "German classified ads platform"
    },
    {
        "Name": "Chrono24",
        "URL": "https://www.chrono24.de",
        "Domain": "chrono24.de",
        "Type": "Marketplace",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 3,
        "Search_URL_Template": "https://www.chrono24.de/search/index.htm?query={manufacturer}+{model}",
        "Listing_Selector": "article.article-item",
        "Title_Selector": ".text-bold",
        "Price_Selector": ".article-item-price",
        "Link_Selector": "a.article-item-link",
        "Notes": "Major watch marketplace"
    },
    {
        "Name": "Chronext",
        "URL": "https://www.chronext.de",
        "Domain": "chronext.de",
        "Type": "Marketplace",
        "Scraper_Type": "Dynamic",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 3,
        "Search_URL_Template": "https://www.chronext.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".product-tile",
        "Title_Selector": ".product-name",
        "Price_Selector": ".product-price",
        "Link_Selector": "a.product-link",
        "Notes": "Premium watch marketplace"
    },
    {
        "Name": "Uhrinstinkt",
        "URL": "https://www.uhrinstinkt.de",
        "Domain": "uhrinstinkt.de",
        "Type": "Marketplace",
        "Scraper_Type": "Static",
        "Active": True,
        "Requires_Auth": False,
        "Rate_Limit_Seconds": 2,
        "Search_URL_Template": "https://www.uhrinstinkt.de/search?q={manufacturer}+{model}",
        "Listing_Selector": ".watch",
        "Title_Selector": ".watch-title",
        "Price_Selector": ".watch-price",
        "Link_Selector": "a",
        "Notes": "German watch marketplace"
    },
]


def create_databases():
    """Create all Notion databases and populate Sources"""

    print("=" * 70)
    print("🚀 Watch Service - Notion Database Setup")
    print("=" * 70)
    print()

    # Get Notion API key
    notion_api_key = os.getenv('NOTION_API_KEY')
    if not notion_api_key:
        print("NOTION_API_KEY not found in environment.")
        notion_api_key = getpass("Enter your Notion API Key: ")

    client = Client(auth=notion_api_key)

    # Test connection
    try:
        print("Testing Notion connection...")
        client.users.me()
        print("✅ Connected to Notion successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to connect to Notion: {e}")
        sys.exit(1)

    # Get parent page ID
    print("Enter the Notion page ID where databases should be created")
    print("(Find it in the URL: notion.so/<workspace>/<PAGE_ID>)")
    parent_page_id = input("Parent Page ID: ").strip()

    if not parent_page_id:
        print("❌ Parent page ID is required")
        sys.exit(1)

    # Clean page ID (remove hyphens if present)
    parent_page_id = parent_page_id.replace('-', '')

    print()
    print("Creating databases...")
    print()

    # 1. Create Sources DB
    print("1️⃣  Creating Sources database...")
    sources_db = create_sources_db(client, parent_page_id)
    print(f"✅ Sources DB created: {sources_db['id']}")
    print()

    # 2. Create Search Criteria DB
    print("2️⃣  Creating Watch_Search_Criteria database...")
    criteria_db = create_search_criteria_db(client, parent_page_id)
    print(f"✅ Search Criteria DB created: {criteria_db['id']}")
    print()

    # 3. Create Listings DB
    print("3️⃣  Creating Watch_Listings database...")
    listings_db = create_listings_db(client, parent_page_id)
    print(f"✅ Listings DB created: {listings_db['id']}")
    print()

    # 4. Create Sync History DB
    print("4️⃣  Creating Sync_History database...")
    sync_db = create_sync_history_db(client, parent_page_id)
    print(f"✅ Sync History DB created: {sync_db['id']}")
    print()

    # 5. Populate Sources DB
    print("5️⃣  Populating Sources database with 17 sources...")
    populate_sources(client, sources_db['id'])
    print(f"✅ Added {len(SOURCES_DATA)} sources to database")
    print()

    # Update .env file
    print("6️⃣  Updating .env file with database IDs...")
    update_env_file(
        sources_db['id'],
        criteria_db['id'],
        listings_db['id'],
        sync_db['id'],
        notion_api_key
    )
    print("✅ .env file updated")
    print()

    print("=" * 70)
    print("🎉 Setup completed successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review databases in Notion")
    print("2. Add search criteria in Watch_Search_Criteria database")
    print("3. Configure credentials in .env file")
    print("4. Run: python3 watch_searcher.py")
    print()


def create_sources_db(client, parent_id):
    """Create Sources database"""
    return client.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Sources"}}],
        properties={
            "Name": {"title": {}},
            "URL": {"url": {}},
            "Domain": {"rich_text": {}},
            "Type": {"select": {"options": [
                {"name": "Dealer", "color": "blue"},
                {"name": "Forum", "color": "green"},
                {"name": "Marketplace", "color": "purple"}
            ]}},
            "Scraper_Type": {"select": {"options": [
                {"name": "Static", "color": "gray"},
                {"name": "Dynamic", "color": "orange"},
                {"name": "Forum", "color": "green"},
                {"name": "Marketplace", "color": "purple"}
            ]}},
            "Active": {"checkbox": {}},
            "Requires_Auth": {"checkbox": {}},
            "Rate_Limit_Seconds": {"number": {"format": "number"}},
            "Search_URL_Template": {"rich_text": {}},
            "Listing_Selector": {"rich_text": {}},
            "Title_Selector": {"rich_text": {}},
            "Price_Selector": {"rich_text": {}},
            "Link_Selector": {"rich_text": {}},
            "Image_Selector": {"rich_text": {}},
            "Custom_Scraper": {"rich_text": {}},
            "Auth_Username_Env": {"rich_text": {}},
            "Auth_Password_Env": {"rich_text": {}},
            "Last_Successful_Scrape": {"date": {}},
            "Error_Count": {"number": {"format": "number"}},
            "Notes": {"rich_text": {}},
            "Created_At": {"created_time": {}}
        }
    )


def create_search_criteria_db(client, parent_id):
    """Create Watch_Search_Criteria database"""
    return client.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Watch_Search_Criteria"}}],
        properties={
            "Name": {"title": {}},
            "Manufacturer": {"rich_text": {}},
            "Model": {"rich_text": {}},
            "Reference_Number": {"rich_text": {}},
            "Year": {"number": {"format": "number"}},
            "Allowed_Countries": {"multi_select": {"options": [
                {"name": "Germany", "color": "blue"},
                {"name": "Austria", "color": "red"},
                {"name": "Switzerland", "color": "gray"},
                {"name": "Netherlands", "color": "orange"},
                {"name": "Belgium", "color": "yellow"}
            ]}},
            "Active": {"checkbox": {}},
            "Notes": {"rich_text": {}},
            "Created_At": {"created_time": {}}
        }
    )


def create_listings_db(client, parent_id):
    """Create Watch_Listings database"""
    return client.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Watch_Listings"}}],
        properties={
            "Name": {"title": {}},
            "Date_Found": {"date": {}},
            "Manufacturer": {"rich_text": {}},
            "Model": {"rich_text": {}},
            "Reference_Number": {"rich_text": {}},
            "Year": {"number": {"format": "number"}},
            "Condition": {"select": {"options": [
                {"name": "Neu", "color": "green"},
                {"name": "Wie Neu", "color": "blue"},
                {"name": "Sehr Gut", "color": "purple"},
                {"name": "Gut", "color": "yellow"},
                {"name": "Gebraucht", "color": "orange"},
                {"name": "Unbekannt", "color": "gray"}
            ]}},
            "Price": {"number": {"format": "number"}},
            "Currency": {"select": {"options": [
                {"name": "EUR", "color": "blue"},
                {"name": "USD", "color": "green"},
                {"name": "CHF", "color": "red"},
                {"name": "GBP", "color": "purple"}
            ]}},
            "Location": {"rich_text": {}},
            "Country": {"rich_text": {}},
            "Link": {"url": {}},
            "Seller_Name": {"rich_text": {}},
            "Seller_URL": {"url": {}},
            "Source": {"select": {"options": [
                {"name": source["Name"], "color": "gray"} for source in SOURCES_DATA
            ]}},
            "Source_Type": {"select": {"options": [
                {"name": "Dealer", "color": "blue"},
                {"name": "Forum", "color": "green"},
                {"name": "Marketplace", "color": "purple"}
            ]}},
            "Availability": {"select": {"options": [
                {"name": "Available", "color": "green"},
                {"name": "Sold", "color": "red"},
                {"name": "Unknown", "color": "gray"}
            ]}},
            "Sold_At": {"date": {}},
            "Last_Checked": {"date": {}},
            "URL_Hash": {"rich_text": {}},
            "Created_At": {"created_time": {}}
        }
    )


def create_sync_history_db(client, parent_id):
    """Create Sync_History database"""
    return client.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Sync_History"}}],
        properties={
            "Name": {"title": {}},
            "Date": {"date": {}},
            "Status": {"select": {"options": [
                {"name": "Success", "color": "green"},
                {"name": "Partial", "color": "yellow"},
                {"name": "Failed", "color": "red"}
            ]}},
            "Sources_Checked": {"number": {"format": "number"}},
            "Sources_Failed": {"number": {"format": "number"}},
            "Listings_Found": {"number": {"format": "number"}},
            "Listings_Saved": {"number": {"format": "number"}},
            "Duplicates_Skipped": {"number": {"format": "number"}},
            "Duration_Seconds": {"number": {"format": "number"}},
            "Error_Message": {"rich_text": {}}
        }
    )


def populate_sources(client, db_id):
    """Populate Sources database with initial data"""
    for source in SOURCES_DATA:
        properties = {
            "Name": {"title": [{"text": {"content": source["Name"]}}]},
            "URL": {"url": source["URL"]},
            "Domain": {"rich_text": [{"text": {"content": source["Domain"]}}]},
            "Type": {"select": {"name": source["Type"]}},
            "Scraper_Type": {"select": {"name": source["Scraper_Type"]}},
            "Active": {"checkbox": source["Active"]},
            "Requires_Auth": {"checkbox": source["Requires_Auth"]},
            "Rate_Limit_Seconds": {"number": source["Rate_Limit_Seconds"]},
            "Search_URL_Template": {"rich_text": [{"text": {"content": source["Search_URL_Template"]}}]},
            "Listing_Selector": {"rich_text": [{"text": {"content": source.get("Listing_Selector", "")}}]},
            "Title_Selector": {"rich_text": [{"text": {"content": source.get("Title_Selector", "")}}]},
            "Price_Selector": {"rich_text": [{"text": {"content": source.get("Price_Selector", "")}}]},
            "Link_Selector": {"rich_text": [{"text": {"content": source.get("Link_Selector", "")}}]},
            "Notes": {"rich_text": [{"text": {"content": source.get("Notes", "")}}]}
        }

        # Add auth fields if present
        if source.get("Auth_Username_Env"):
            properties["Auth_Username_Env"] = {"rich_text": [{"text": {"content": source["Auth_Username_Env"]}}]}
        if source.get("Auth_Password_Env"):
            properties["Auth_Password_Env"] = {"rich_text": [{"text": {"content": source["Auth_Password_Env"]}}]}

        client.pages.create(
            parent={"database_id": db_id},
            properties=properties
        )
        print(f"  ✓ Added: {source['Name']}")


def update_env_file(sources_id, criteria_id, listings_id, sync_id, api_key):
    """Update .env file with database IDs"""
    env_path = ".env"

    # Read existing .env or create from .env.example
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    elif os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            lines = f.readlines()
    else:
        lines = []

    # Update or add database IDs
    updates = {
        'NOTION_API_KEY': api_key,
        'SOURCES_DB_ID': sources_id,
        'SEARCH_CRITERIA_DB_ID': criteria_id,
        'LISTINGS_DB_ID': listings_id,
        'SYNC_HISTORY_DB_ID': sync_id
    }

    new_lines = []
    updated_keys = set()

    for line in lines:
        updated = False
        for key, value in updates.items():
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated_keys.add(key)
                updated = True
                break
        if not updated:
            new_lines.append(line)

    # Add missing keys
    for key, value in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(new_lines)


if __name__ == '__main__':
    create_databases()
