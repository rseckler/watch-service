"""Test if new Sources DB works like Blackfire"""
from dotenv import load_dotenv
import os
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

# Your new Sources DB
new_sources_db_id = "2fa708a3de9580eb8bebdcc9afec8614"

print("🧪 Testing new Sources DB with simple page creation...")
print()

try:
    # Try to create a TEST page with just Name
    test_page = client.pages.create(
        parent={"database_id": new_sources_db_id},
        properties={
            "Name": {
                "title": [{"text": {"content": "TEST - Cologne Watch"}}]
            }
        }
    )

    print("✅ SUCCESS! Page created!")
    print(f"Page ID: {test_page['id']}")
    print()
    print("🎉 DEINE DATENBANK FUNKTIONIERT!")
    print()
    print("Das Problem war: Ich habe die falschen Property-Namen verwendet!")
    print("Lösung: Ich muss die EXAKTEN Spaltennamen aus deiner DB verwenden!")

except Exception as e:
    print(f"❌ Error: {e}")
    print()

    # Try to understand what properties exist
    print("Lass mich die Spalten in deiner DB auflisten...")
    print("Öffne bitte die Sources DB in Notion und sag mir:")
    print("1. Wie heißt die erste Spalte? (Titel-Spalte)")
    print("2. Welche anderen Spalten hast du angelegt?")
