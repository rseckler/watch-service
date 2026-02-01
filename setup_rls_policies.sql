-- Setup Row Level Security (RLS) policies for Watch Service
-- This allows the web app (using anon key) to access watch_* tables
--
-- HOW TO USE:
-- 1. Go to https://supabase.com/dashboard/project/lglvuiuwbrhiqvxcriwa/sql/new
-- 2. Copy-paste this entire file
-- 3. Click "Run" button
-- 4. Done! Web app will work immediately

-- Enable RLS on all tables (if not already enabled)
ALTER TABLE watch_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE watch_search_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE watch_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE watch_sync_history ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Allow public read access" ON watch_sources;
DROP POLICY IF EXISTS "Allow public write access" ON watch_sources;
DROP POLICY IF EXISTS "Allow public read access" ON watch_search_criteria;
DROP POLICY IF EXISTS "Allow public write access" ON watch_search_criteria;
DROP POLICY IF EXISTS "Allow public read access" ON watch_listings;
DROP POLICY IF EXISTS "Allow public write access" ON watch_listings;
DROP POLICY IF EXISTS "Allow public read access" ON watch_sync_history;
DROP POLICY IF EXISTS "Allow public write access" ON watch_sync_history;

-- ====================================================================
-- WATCH SOURCES - Allow full public access
-- ====================================================================

CREATE POLICY "Allow public read access" ON watch_sources
FOR SELECT
USING (true);

CREATE POLICY "Allow public write access" ON watch_sources
FOR ALL
USING (true)
WITH CHECK (true);

-- ====================================================================
-- WATCH SEARCH CRITERIA - Allow full public access
-- ====================================================================

CREATE POLICY "Allow public read access" ON watch_search_criteria
FOR SELECT
USING (true);

CREATE POLICY "Allow public write access" ON watch_search_criteria
FOR ALL
USING (true)
WITH CHECK (true);

-- ====================================================================
-- WATCH LISTINGS - Allow full public access
-- ====================================================================

CREATE POLICY "Allow public read access" ON watch_listings
FOR SELECT
USING (true);

CREATE POLICY "Allow public write access" ON watch_listings
FOR ALL
USING (true)
WITH CHECK (true);

-- ====================================================================
-- WATCH SYNC HISTORY - Allow full public access
-- ====================================================================

CREATE POLICY "Allow public read access" ON watch_sync_history
FOR SELECT
USING (true);

CREATE POLICY "Allow public write access" ON watch_sync_history
FOR ALL
USING (true)
WITH CHECK (true);

-- ====================================================================
-- DONE!
-- ====================================================================
-- The web app can now read and write to all watch_* tables
-- Test it: https://watch-service.vercel.app/sources
