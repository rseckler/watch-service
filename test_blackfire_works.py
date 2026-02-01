"""Test if we can actually CREATE pages in Blackfire database"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

blackfire_db_id = "2f3708a3-de95-807b-88c4-ca0463fd07fb"

print("🧪 Testing if Blackfire DB allows page creation...")
print()

try:
    # Get database schema first
    db = client.databases.retrieve(database_id=blackfire_db_id)

    print(f"Database: {db.get('title', [{}])[0].get('plain_text', 'Blackfire')}")
    print(f"Has data_sources: {'data_sources' in db}")
    print(f"Has properties: {'properties' in db}")
    print()

    # Try to create a TEST page
    print("Attempting to create test page...")

    test_page = client.pages.create(
        parent={"database_id": blackfire_db_id},
        properties={
            "Name": {
                "title": [{"text": {"content": "TEST - Watch Service Test"}}]
            }
        }
    )

    print("✅ SUCCESS! Page created in Blackfire DB!")
    print(f"Page ID: {test_page['id']}")
    print()
    print("🎉 DAS BEDEUTET: Blackfire DB funktioniert TROTZ Data Sources!")
    print("🎉 Wir können das gleiche System verwenden!")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Blackfire DB hat ein anderes Format...")
