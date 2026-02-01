-- Watch Service Database Schema
-- Run this in Vercel Postgres/Neon SQL Editor

-- ====================================================================
-- TABLE 1: watch_sources
-- ====================================================================

CREATE TABLE IF NOT EXISTS watch_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  url TEXT NOT NULL,
  domain VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL CHECK (type IN ('Dealer', 'Forum', 'Marketplace')),
  scraper_type VARCHAR(50) NOT NULL CHECK (scraper_type IN ('Static', 'Dynamic', 'Forum', 'Marketplace')),
  active BOOLEAN DEFAULT true,
  requires_auth BOOLEAN DEFAULT false,
  rate_limit_seconds INTEGER DEFAULT 2,
  search_url_template TEXT,
  listing_selector TEXT,
  title_selector TEXT,
  price_selector TEXT,
  link_selector TEXT,
  image_selector TEXT,
  custom_scraper VARCHAR(255),
  auth_username_env VARCHAR(100),
  auth_password_env VARCHAR(100),
  last_successful_scrape TIMESTAMP,
  error_count INTEGER DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sources_active ON watch_sources(active);
CREATE INDEX IF NOT EXISTS idx_sources_type ON watch_sources(type);

-- ====================================================================
-- TABLE 2: watch_search_criteria
-- ====================================================================

CREATE TABLE IF NOT EXISTS watch_search_criteria (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  manufacturer VARCHAR(100) NOT NULL,
  model VARCHAR(100) NOT NULL,
  reference_number VARCHAR(50),
  year INTEGER,
  allowed_countries TEXT[], -- Array of countries
  active BOOLEAN DEFAULT true,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_criteria_active ON watch_search_criteria(active);
CREATE INDEX IF NOT EXISTS idx_criteria_manufacturer ON watch_search_criteria(manufacturer);

-- ====================================================================
-- TABLE 3: watch_listings
-- ====================================================================

CREATE TABLE IF NOT EXISTS watch_listings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  date_found TIMESTAMP DEFAULT NOW(),
  manufacturer VARCHAR(100),
  model VARCHAR(100),
  reference_number VARCHAR(50),
  year INTEGER,
  condition VARCHAR(50),
  price NUMERIC(10, 2),
  currency VARCHAR(10) DEFAULT 'EUR',
  location VARCHAR(255),
  country VARCHAR(100),
  link TEXT NOT NULL,
  seller_name VARCHAR(255),
  seller_url TEXT,
  source VARCHAR(100),
  source_type VARCHAR(50),
  availability VARCHAR(20) DEFAULT 'Available' CHECK (availability IN ('Available', 'Sold', 'Unknown')),
  sold_at TIMESTAMP,
  last_checked TIMESTAMP DEFAULT NOW(),
  url_hash VARCHAR(64) UNIQUE,
  search_criteria_id UUID REFERENCES watch_search_criteria(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_listings_availability ON watch_listings(availability);
CREATE INDEX IF NOT EXISTS idx_listings_source ON watch_listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_date_found ON watch_listings(date_found DESC);
CREATE INDEX IF NOT EXISTS idx_listings_url_hash ON watch_listings(url_hash);

-- ====================================================================
-- TABLE 4: watch_sync_history
-- ====================================================================

CREATE TABLE IF NOT EXISTS watch_sync_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  date TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) CHECK (status IN ('Success', 'Partial', 'Failed')),
  sources_checked INTEGER DEFAULT 0,
  sources_failed INTEGER DEFAULT 0,
  listings_found INTEGER DEFAULT 0,
  listings_saved INTEGER DEFAULT 0,
  duplicates_skipped INTEGER DEFAULT 0,
  duration_seconds INTEGER,
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_sync_history_date ON watch_sync_history(date DESC);

-- ====================================================================
-- DONE
-- ====================================================================

-- Verify tables created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'watch_%';
