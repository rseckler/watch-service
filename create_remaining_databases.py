"""Create the remaining 3 databases"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

parent_page_id = "2fa708a3de95800d9a80cd68d60922f6"

print("🔨 Creating 3 databases...")
print()

databases_to_create = [
    {
        "name": "Watch_Search_Criteria",
        "properties": {
            "Name": {"title": {}},
            "Manufacturer": {"rich_text": {}},
            "Model": {"rich_text": {}},
            "Reference_Number": {"rich_text": {}},
            "Year": {"number": {"format": "number"}},
            "Allowed_Countries": {"multi_select": {"options": [
                {"name": "Germany", "color": "blue"},
                {"name": "Austria", "color": "red"},
                {"name": "Switzerland", "color": "gray"},
                {"name": "Netherlands", "color": "orange"},
                {"name": "Belgium", "color": "yellow"}
            ]}},
            "Active": {"checkbox": {}},
            "Notes": {"rich_text": {}},
        }
    },
    {
        "name": "Watch_Listings",
        "properties": {
            "Name": {"title": {}},
            "Date_Found": {"date": {}},
            "Manufacturer": {"rich_text": {}},
            "Model": {"rich_text": {}},
            "Reference_Number": {"rich_text": {}},
            "Year": {"number": {"format": "number"}},
            "Condition": {"select": {"options": [
                {"name": "Neu", "color": "green"},
                {"name": "Wie Neu", "color": "blue"},
                {"name": "Sehr Gut", "color": "purple"},
                {"name": "Gut", "color": "yellow"},
                {"name": "Gebraucht", "color": "orange"},
                {"name": "Unbekannt", "color": "gray"}
            ]}},
            "Price": {"number": {"format": "number"}},
            "Currency": {"select": {"options": [
                {"name": "EUR", "color": "blue"},
                {"name": "USD", "color": "green"},
                {"name": "CHF", "color": "red"},
                {"name": "GBP", "color": "purple"}
            ]}},
            "Location": {"rich_text": {}},
            "Country": {"rich_text": {}},
            "Link": {"url": {}},
            "Seller_Name": {"rich_text": {}},
            "Source": {"select": {"options": [
                {"name": "Cologne Watch", "color": "gray"},
                {"name": "Watch Vice", "color": "gray"},
                {"name": "Unknown", "color": "gray"}
            ]}},
            "Availability": {"select": {"options": [
                {"name": "Available", "color": "green"},
                {"name": "Sold", "color": "red"},
                {"name": "Unknown", "color": "gray"}
            ]}},
            "Sold_At": {"date": {}},
            "URL_Hash": {"rich_text": {}},
        }
    },
    {
        "name": "Sync_History",
        "properties": {
            "Name": {"title": {}},
            "Date": {"date": {}},
            "Status": {"select": {"options": [
                {"name": "Success", "color": "green"},
                {"name": "Partial", "color": "yellow"},
                {"name": "Failed", "color": "red"}
            ]}},
            "Sources_Checked": {"number": {"format": "number"}},
            "Sources_Failed": {"number": {"format": "number"}},
            "Listings_Found": {"number": {"format": "number"}},
            "Listings_Saved": {"number": {"format": "number"}},
            "Duplicates_Skipped": {"number": {"format": "number"}},
            "Duration_Seconds": {"number": {"format": "number"}},
            "Error_Message": {"rich_text": {}},
        }
    }
]

created_dbs = {}

for db_config in databases_to_create:
    try:
        print(f"Creating {db_config['name']}...")

        db = client.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": db_config['name']}}],
            properties=db_config['properties']
        )

        db_id = db['id']
        created_dbs[db_config['name']] = db_id

        print(f"  ✅ Created: {db_id}")

    except Exception as e:
        print(f"  ❌ Error: {e}")

print()
print("=" * 70)
print("📋 DATABASE IDs:")
print("=" * 70)

# Show existing Sources DB
print(f"SOURCES_DB_ID=2fa708a3de9580eb8bebdcc9afec8614")

# Show newly created DBs
for name, db_id in created_dbs.items():
    env_name = name.upper() + "_DB_ID"
    print(f"{env_name}={db_id}")

print()
print("🔧 Nächster Schritt:")
print("1. Teile alle 3 neuen DBs mit 'Watch Service' Integration in Notion")
print("2. Dann trage ich die IDs in die .env ein")
print("3. Fertig!")
