from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

# Blackfire database ID
blackfire_db_id = "2f3708a3-de95-807b-88c4-ca0463fd07fb"

print("🔍 Testing Blackfire_automation Notion database...")
print()

try:
    db = client.databases.retrieve(database_id=blackfire_db_id)

    if 'properties' in db:
        print("✅ PERFEKT! Blackfire DB has normal properties!")
        print()
        print("This means we can CREATE databases that work!")
        print("Let me create new Watch Service databases using the same method...")
    else:
        print("❌ Blackfire DB also has Data Sources")

except Exception as e:
    print(f"Error: {e}")
