from dotenv import load_dotenv
import os
import json
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

print("🔍 Verifying Sources DB properties...")
print()

try:
    # Get database schema
    db = client.databases.retrieve(database_id=os.getenv('SOURCES_DB_ID'))

    print("Database response keys:", list(db.keys()))
    print()

    # Check different possible locations for properties
    if 'properties' in db:
        print("✅ Properties found in 'properties':")
        for prop_name in sorted(db['properties'].keys()):
            prop_type = db['properties'][prop_name]['type']
            print(f"  - {prop_name:30} ({prop_type})")
    elif 'schema' in db:
        print("✅ Properties found in 'schema':")
        for prop_name in sorted(db['schema'].keys()):
            prop_type = db['schema'][prop_name]['type']
            print(f"  - {prop_name:30} ({prop_type})")
    else:
        print("⚠️ Properties not found in expected location")
        print("\nFull database structure:")
        print(json.dumps(db, indent=2))

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
