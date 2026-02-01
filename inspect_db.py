from dotenv import load_dotenv
import os
import json
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

# Get Sources DB schema
try:
    db = client.databases.retrieve(database_id=os.getenv('SOURCES_DB_ID'))
    print("\n✅ Database retrieved successfully")
    print("\nDatabase keys:", list(db.keys()))

    if 'properties' in db:
        print("\n✅ Properties found:")
        for prop_name in sorted(db['properties'].keys()):
            prop_type = db['properties'][prop_name]['type']
            print(f"  - {prop_name:30} ({prop_type})")
    else:
        print("\n⚠️ No 'properties' key found")
        print("Full response:")
        print(json.dumps(db, indent=2))
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
