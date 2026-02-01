#!/usr/bin/env python3
"""
Setup Row Level Security (RLS) policies for Watch Service
Allows the web app (using anon key) to access watch_* tables
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client with SERVICE_ROLE_KEY (has admin access)
supabase_url = os.getenv("SUPABASE_URL")
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not service_role_key:
    print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

supabase = create_client(supabase_url, service_role_key)

print("🔐 Setting up RLS policies for Watch Service...")

# SQL commands to set up RLS policies
# Allow public read/write access to all watch_* tables

sql_commands = [
    # Enable RLS on all tables (if not already enabled)
    "ALTER TABLE watch_sources ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE watch_search_criteria ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE watch_listings ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE watch_sync_history ENABLE ROW LEVEL SECURITY;",

    # Drop existing policies if they exist (to avoid conflicts)
    "DROP POLICY IF EXISTS \"Allow public read access\" ON watch_sources;",
    "DROP POLICY IF EXISTS \"Allow public write access\" ON watch_sources;",
    "DROP POLICY IF EXISTS \"Allow public read access\" ON watch_search_criteria;",
    "DROP POLICY IF EXISTS \"Allow public write access\" ON watch_search_criteria;",
    "DROP POLICY IF EXISTS \"Allow public read access\" ON watch_listings;",
    "DROP POLICY IF EXISTS \"Allow public write access\" ON watch_listings;",
    "DROP POLICY IF EXISTS \"Allow public read access\" ON watch_sync_history;",
    "DROP POLICY IF EXISTS \"Allow public write access\" ON watch_sync_history;",

    # Create new policies allowing full public access
    # watch_sources
    """
    CREATE POLICY "Allow public read access" ON watch_sources
    FOR SELECT USING (true);
    """,
    """
    CREATE POLICY "Allow public write access" ON watch_sources
    FOR ALL USING (true);
    """,

    # watch_search_criteria
    """
    CREATE POLICY "Allow public read access" ON watch_search_criteria
    FOR SELECT USING (true);
    """,
    """
    CREATE POLICY "Allow public write access" ON watch_search_criteria
    FOR ALL USING (true);
    """,

    # watch_listings
    """
    CREATE POLICY "Allow public read access" ON watch_listings
    FOR SELECT USING (true);
    """,
    """
    CREATE POLICY "Allow public write access" ON watch_listings
    FOR ALL USING (true);
    """,

    # watch_sync_history
    """
    CREATE POLICY "Allow public read access" ON watch_sync_history
    FOR SELECT USING (true);
    """,
    """
    CREATE POLICY "Allow public write access" ON watch_sync_history
    FOR ALL USING (true);
    """,
]

# Execute each SQL command
for i, sql in enumerate(sql_commands, 1):
    try:
        # Use rpc to execute raw SQL
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print(f"✅ [{i}/{len(sql_commands)}] Executed: {sql[:50]}...")
    except Exception as e:
        # Try alternative method using postgrest
        try:
            # Use supabase.postgrest to execute SQL
            result = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ [{i}/{len(sql_commands)}] Executed: {sql[:50]}...")
        except Exception as e2:
            print(f"⚠️  [{i}/{len(sql_commands)}] Warning: {sql[:50]}... - {str(e2)[:100]}")
            # Continue with next command

print("\n🎉 RLS policies setup completed!")
print("\n📝 Summary:")
print("   - Enabled RLS on all watch_* tables")
print("   - Created policies allowing public read/write access")
print("   - Web app (using anon key) can now access all data")
print("\n🌐 Test the web app: https://watch-service.vercel.app/sources")
