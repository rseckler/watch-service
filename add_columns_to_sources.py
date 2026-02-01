"""Add columns/properties to Sources database via API"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

sources_db_id = "2fa708a3de9580eb8bebdcc9afec8614"

print("🔧 Adding columns to Sources database...")
print()

try:
    # Try to add properties via databases.update()
    response = client.databases.update(
        database_id=sources_db_id,
        properties={
            "URL": {"url": {}},
            "Domain": {"rich_text": {}},
            "Type": {"select": {"options": [
                {"name": "Dealer", "color": "blue"},
                {"name": "Forum", "color": "green"},
                {"name": "Marketplace", "color": "purple"}
            ]}},
            "Scraper_Type": {"select": {"options": [
                {"name": "Static", "color": "gray"},
                {"name": "Dynamic", "color": "orange"}
            ]}},
            "Active": {"checkbox": {}},
            "Requires_Auth": {"checkbox": {}},
            "Rate_Limit_Seconds": {"number": {"format": "number"}},
            "Search_URL_Template": {"rich_text": {}},
            "Listing_Selector": {"rich_text": {}},
            "Title_Selector": {"rich_text": {}},
            "Price_Selector": {"rich_text": {}},
            "Link_Selector": {"rich_text": {}},
            "Notes": {"rich_text": {}},
        }
    )

    print("✅ SUCCESS! Columns added via API!")
    print()
    print("Prüfe in Notion, ob die Spalten jetzt da sind!")

except Exception as e:
    print(f"❌ API kann keine Spalten hinzufügen: {e}")
    print()
    print("Bei Data Sources DBs müssen Spalten manuell in Notion angelegt werden.")
    print()
    print("SCHNELLSTE LÖSUNG:")
    print("1. Importiere die CSV die ich erstellt habe (sources_import.csv)")
    print("2. Notion erstellt automatisch alle Spalten beim Import!")
