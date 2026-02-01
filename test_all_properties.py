"""Test if all properties work now"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

sources_db_id = "2fa708a3de9580eb8bebdcc9afec8614"

print("🧪 Testing if all properties work...")
print()

try:
    # Try to create a complete test entry
    test_page = client.pages.create(
        parent={"database_id": sources_db_id},
        properties={
            "Name": {"title": [{"text": {"content": "Cologne Watch"}}]},
            "URL": {"url": "https://www.colognewatch.de"},
            "Domain": {"rich_text": [{"text": {"content": "colognewatch.de"}}]},
            "Type": {"select": {"name": "Dealer"}},
            "Scraper_Type": {"select": {"name": "Static"}},
            "Active": {"checkbox": True},
            "Requires_Auth": {"checkbox": False},
            "Rate_Limit_Seconds": {"number": 2},
            "Search_URL_Template": {"rich_text": [{"text": {"content": "https://www.colognewatch.de/search?q={manufacturer}+{model}"}}]},
            "Listing_Selector": {"rich_text": [{"text": {"content": ".product-item"}}]},
            "Title_Selector": {"rich_text": [{"text": {"content": ".product-card__title"}}]},
            "Price_Selector": {"rich_text": [{"text": {"content": ".price-item"}}]},
            "Link_Selector": {"rich_text": [{"text": {"content": "a.product-item__link"}}]},
            "Notes": {"rich_text": [{"text": {"content": "German luxury watch dealer"}}]},
        }
    )

    print("✅ PERFEKT! Alle Properties funktionieren!")
    print(f"Page ID: {test_page['id']}")
    print()
    print("🎉 JETZT KANN ICH ALLE 17 SOURCES EINTRAGEN!")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Prüfe in Notion, welche Spalten fehlen...")
