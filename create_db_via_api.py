"""Try to create database via API as child of page"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

parent_page_id = "2fa708a3de95800d9a80cd68d60922f6"

print("🧪 Testing: Creating database via API...")
print(f"Parent Page ID: {parent_page_id}")
print()

try:
    # Try to create a test database
    db = client.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "API Test Database"}}],
        properties={
            "Name": {"title": {}},
            "Test Field": {"rich_text": {}},
        }
    )

    print("✅ Database created via API!")
    print(f"Database ID: {db['id']}")
    print()

    # Check if it has properties
    if 'properties' in db:
        print("🎉 ERFOLG! It has PROPERTIES (not data_sources)!")
        print()
        print("Das bedeutet: Wir können funktionierende DBs über API erstellen!")
        print()
        print("Properties:")
        for prop_name in db['properties'].keys():
            print(f"  - {prop_name}: {db['properties'][prop_name]['type']}")
    else:
        print("❌ Hat keine properties")

except Exception as e:
    print(f"❌ Error: {e}")
