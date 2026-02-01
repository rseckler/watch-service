"""Test if new Watch Service integration can create normal databases"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

# Use the "Watch Service Databases" page
parent_page_id = "2fa708a3de95800d9a80cd68d60922f6"

print("🧪 Testing NEW 'Watch Service' Integration...")
print()

try:
    # Create a test database
    db = client.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "TEST - New Integration DB"}}],
        properties={
            "Name": {"title": {}},
            "URL": {"url": {}},
            "Domain": {"rich_text": {}},
            "Type": {"select": {"options": [
                {"name": "Dealer", "color": "blue"},
                {"name": "Forum", "color": "green"}
            ]}},
            "Active": {"checkbox": {}},
        }
    )

    print("✅ Database created!")
    print(f"Database ID: {db['id']}")
    print()

    # Check if it has PROPERTIES (not data_sources)
    if 'properties' in db and db['properties']:
        print("🎉🎉🎉 ERFOLG! Diese DB hat PROPERTIES! 🎉🎉🎉")
        print()
        print("Properties:")
        for prop_name in db['properties'].keys():
            print(f"  ✓ {prop_name}: {db['properties'][prop_name]['type']}")
        print()
        print("=" * 70)
        print("🚀 DIE NEUE INTEGRATION FUNKTIONIERT PERFEKT!")
        print("🚀 ICH KANN JETZT ALLE DATENBANKEN RICHTIG ERSTELLEN!")
        print("=" * 70)

    elif 'data_sources' in db:
        print("❌ Leider wieder Data Sources...")
        print("Das liegt am Workspace, nicht an der Integration")

    else:
        print("⚠️ Unbekanntes Format")

except Exception as e:
    print(f"❌ Error: {e}")
