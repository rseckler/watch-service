"""Test if we can create pages in the databases"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

print("🧪 Testing page creation in Watch_Listings database...")
print()

try:
    # Try to create a test listing
    test_data = {
        "Name": {"title": [{"text": {"content": "TEST - Rolex Submariner"}}]},
        "Manufacturer": {"rich_text": [{"text": {"content": "Rolex"}}]},
        "Model": {"rich_text": [{"text": {"content": "Submariner"}}]},
        "Price": {"number": 9999},
        "Currency": {"select": {"name": "EUR"}},
        "Source": {"select": {"name": "Cologne Watch"}},
        "Availability": {"select": {"name": "Available"}},
    }

    response = client.pages.create(
        parent={"database_id": os.getenv('LISTINGS_DB_ID')},
        properties=test_data
    )

    print("✅ SUCCESS! Test page created")
    print(f"Page ID: {response['id']}")
    print()
    print("🎉 Die Datenbanken funktionieren! Wir können loslegen!")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("⚠️  Die Data Sources Datenbanken unterstützen keine API-Erstellung von Pages.")
    print("Wir müssen die Datenbanken neu erstellen als normale Notion DBs.")
