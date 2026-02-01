from dotenv import load_dotenv
import os
import json
load_dotenv()

from notion_client import Client
client = Client(auth=os.getenv('NOTION_API_KEY'))

# New database ID
db_id = "2fa708a3de9580eb8bebdcc9afec8614"

print("🔍 Checking newest Sources database...")
print(f"Database ID: {db_id}")
print()

try:
    db = client.databases.retrieve(database_id=db_id)

    print("✅ Database retrieved successfully")
    print()

    # Check if it has 'properties' (good) or 'data_sources' (bad)
    if 'properties' in db:
        print("🎉 PERFEKT! This is a NORMAL database with properties!")
        print()
        print("Properties found:")
        for prop_name in sorted(db['properties'].keys()):
            prop_type = db['properties'][prop_name]['type']
            print(f"  - {prop_name:30} ({prop_type})")
        print()
        print("=" * 70)
        print("✅ DIESE DATENBANK FUNKTIONIERT MIT DER API!")
        print("✅ Du kannst jetzt die anderen 3 DBs genauso erstellen!")
        print("=" * 70)

    elif 'data_sources' in db:
        print("❌ PROBLEM: Dies ist wieder eine Data Sources Datenbank")
        print()
        print("Dein Workspace erstellt automatisch nur Data Sources DBs.")
        print("Empfehlung: Lokale SQLite + Web-UI verwenden")

    else:
        print("⚠️ Unbekanntes Format")

except Exception as e:
    if "Make sure the relevant pages and databases are shared" in str(e):
        print("❌ Datenbank nicht mit Integration geteilt!")
        print()
        print("Bitte: Datenbank öffnen → ⋮ → Connections → 'n8n Hostinger' hinzufügen")
    else:
        print(f"❌ Error: {e}")
