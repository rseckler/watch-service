"""Test alternative page creation methods"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

db_id = "2fa708a3de9580d5b4f0d0d8434c87c2"  # New Sources DB

print("🧪 Testing alternative page creation method...")
print()

try:
    # Try with minimal properties
    response = client.pages.create(
        parent={"database_id": db_id},
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "TEST Entry"
                        }
                    }
                ]
            }
        }
    )

    print("✅ SUCCESS! Page created!")
    print(f"Page ID: {response['id']}")
    print()
    print("🎉 Es funktioniert doch! Wir können Pages erstellen!")

except Exception as e:
    print(f"❌ Failed: {e}")
    print()
    print("📊 Empfehlung: Lokale SQLite Datenbank + CSV Export für Notion")

