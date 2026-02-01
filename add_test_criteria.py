"""
Add test search criteria to Supabase
Creates 2 example watch search criteria for testing
"""
from dotenv import load_dotenv
from core.supabase_client import SupabaseClient

load_dotenv()

print("=" * 70)
print("🔍 Adding Test Search Criteria")
print("=" * 70)
print()

client = SupabaseClient()

# Test criteria to add
TEST_CRITERIA = [
    {
        "name": "Rolex Submariner 116610LN",
        "manufacturer": "Rolex",
        "model": "Submariner",
        "reference_number": "116610LN",
        "year": 2020,
        "allowed_countries": ["Germany", "Austria", "Switzerland"],
        "active": True,
        "notes": "Black dial version - test criteria"
    },
    {
        "name": "Omega Speedmaster Moonwatch",
        "manufacturer": "Omega",
        "model": "Speedmaster",
        "reference_number": "311.30.42.30.01.005",
        "year": 2019,
        "allowed_countries": ["Germany", "Austria"],
        "active": True,
        "notes": "Moonwatch Professional - test criteria"
    }
]

try:
    for criteria in TEST_CRITERIA:
        result = client.client.table('watch_search_criteria').insert(criteria).execute()
        print(f"✅ Added: {criteria['name']}")

    print()
    print("=" * 70)
    print("🎉 Test Criteria Added Successfully!")
    print("=" * 70)
    print()
    print("Next: Run test_complete_system.py to test the full flow")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("💡 Criteria might already exist. Check your Supabase table:")
    print("   https://app.supabase.com/project/lglvuiuwbrhiqvxcriwa/editor")
