"""
Populate Sources database with 17 pre-configured sources
"""
from dotenv import load_dotenv
import os
import sys

# Import from setup script
from setup_notion_databases import SOURCES_DATA, populate_sources
from notion_client import Client

load_dotenv()

print("=" * 70)
print("🔄 Populating Sources Database with 17 Sources")
print("=" * 70)
print()

client = Client(auth=os.getenv('NOTION_API_KEY'))
db_id = os.getenv('SOURCES_DB_ID')

try:
    populate_sources(client, db_id)
    print()
    print("=" * 70)
    print(f"✅ Successfully added {len(SOURCES_DATA)} sources!")
    print("=" * 70)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
