"""
Add properties to existing Notion databases
Fixes the issue where databases were created without properties
"""
from dotenv import load_dotenv
import os
from notion_client import Client

load_dotenv()

client = Client(auth=os.getenv('NOTION_API_KEY'))

print("=" * 70)
print("🔧 Adding Properties to Notion Databases")
print("=" * 70)
print()

# === 1. ADD PROPERTIES TO SOURCES DB ===
print("1️⃣  Adding properties to Sources database...")
try:
    client.databases.update(
        database_id=os.getenv('SOURCES_DB_ID'),
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
        }
    )
    print("✅ Sources properties added")
except Exception as e:
    print(f"❌ Error: {e}")

# === 2. ADD PROPERTIES TO SEARCH CRITERIA DB ===
print("\n2️⃣  Adding properties to Watch_Search_Criteria database...")
try:
    client.databases.update(
        database_id=os.getenv('SEARCH_CRITERIA_DB_ID'),
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
        }
    )
    print("✅ Watch_Search_Criteria properties added")
except Exception as e:
    print(f"❌ Error: {e}")

# === 3. ADD PROPERTIES TO LISTINGS DB ===
print("\n3️⃣  Adding properties to Watch_Listings database...")
try:
    client.databases.update(
        database_id=os.getenv('LISTINGS_DB_ID'),
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
                {"name": "Cologne Watch", "color": "gray"},
                {"name": "Watch Vice", "color": "gray"},
                {"name": "Watch.de", "color": "gray"},
                {"name": "Marks Uhren", "color": "gray"},
                {"name": "Rothfuss Watches", "color": "gray"},
                {"name": "Karmann Watches", "color": "gray"},
                {"name": "Eupen Feine Uhren", "color": "gray"},
                {"name": "G-Abriel", "color": "gray"},
                {"name": "Bachmann & Scher", "color": "gray"},
                {"name": "Uhrforum.de", "color": "gray"},
                {"name": "WatchLounge Forum", "color": "gray"},
                {"name": "Uhr-Forum.org", "color": "gray"},
                {"name": "eBay.de", "color": "gray"},
                {"name": "Kleinanzeigen.de", "color": "gray"},
                {"name": "Chrono24", "color": "gray"},
                {"name": "Chronext", "color": "gray"},
                {"name": "Uhrinstinkt", "color": "gray"},
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
        }
    )
    print("✅ Watch_Listings properties added")
except Exception as e:
    print(f"❌ Error: {e}")

# === 4. ADD PROPERTIES TO SYNC HISTORY DB ===
print("\n4️⃣  Adding properties to Sync_History database...")
try:
    client.databases.update(
        database_id=os.getenv('SYNC_HISTORY_DB_ID'),
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
            "Error_Message": {"rich_text": {}},
        }
    )
    print("✅ Sync_History properties added")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("🎉 All properties added successfully!")
print("=" * 70)
print("\nNext step: Run populate_sources.py to add 17 sources")
