"""
Setup Supabase database - Create tables and populate with initial data
Run this ONCE to initialize the database
"""
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 70)
print("🚀 Watch Service - Supabase Setup")
print("=" * 70)
print()

# SQL to create all 4 tables
CREATE_TABLES_SQL = """
-- 1. SOURCES TABLE
CREATE TABLE IF NOT EXISTS watch_sources (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Dealer', 'Forum', 'Marketplace')),
    scraper_type TEXT NOT NULL CHECK (scraper_type IN ('Static', 'Dynamic')),
    active BOOLEAN DEFAULT true,
    requires_auth BOOLEAN DEFAULT false,
    rate_limit_seconds INTEGER DEFAULT 2,
    search_url_template TEXT NOT NULL,
    listing_selector TEXT,
    title_selector TEXT,
    price_selector TEXT,
    link_selector TEXT,
    image_selector TEXT,
    custom_scraper TEXT,
    auth_username_env TEXT,
    auth_password_env TEXT,
    last_successful_scrape TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. SEARCH CRITERIA TABLE
CREATE TABLE IF NOT EXISTS watch_search_criteria (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    reference_number TEXT,
    year INTEGER,
    allowed_countries TEXT[], -- Array of countries
    active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. WATCH LISTINGS TABLE
CREATE TABLE IF NOT EXISTS watch_listings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    date_found TIMESTAMP DEFAULT NOW(),
    manufacturer TEXT,
    model TEXT,
    reference_number TEXT,
    year INTEGER,
    condition TEXT CHECK (condition IN ('Neu', 'Wie Neu', 'Sehr Gut', 'Gut', 'Gebraucht', 'Unbekannt')),
    price DECIMAL(10,2),
    currency TEXT DEFAULT 'EUR',
    location TEXT,
    country TEXT,
    link TEXT NOT NULL,
    seller_name TEXT,
    seller_url TEXT,
    source TEXT NOT NULL,
    source_type TEXT CHECK (source_type IN ('Dealer', 'Forum', 'Marketplace')),
    availability TEXT DEFAULT 'Available' CHECK (availability IN ('Available', 'Sold', 'Unknown')),
    sold_at TIMESTAMP,
    last_checked TIMESTAMP DEFAULT NOW(),
    url_hash TEXT UNIQUE NOT NULL,
    search_criteria_id UUID REFERENCES watch_search_criteria(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. SYNC HISTORY TABLE
CREATE TABLE IF NOT EXISTS watch_sync_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    date TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'Success' CHECK (status IN ('Success', 'Partial', 'Failed')),
    sources_checked INTEGER DEFAULT 0,
    sources_failed INTEGER DEFAULT 0,
    listings_found INTEGER DEFAULT 0,
    listings_saved INTEGER DEFAULT 0,
    duplicates_skipped INTEGER DEFAULT 0,
    duration_seconds INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_watch_listings_availability ON watch_listings(availability);
CREATE INDEX IF NOT EXISTS idx_watch_listings_source ON watch_listings(source);
CREATE INDEX IF NOT EXISTS idx_watch_listings_date_found ON watch_listings(date_found DESC);
CREATE INDEX IF NOT EXISTS idx_watch_listings_url_hash ON watch_listings(url_hash);
CREATE INDEX IF NOT EXISTS idx_watch_sources_active ON watch_sources(active);
CREATE INDEX IF NOT EXISTS idx_watch_search_criteria_active ON watch_search_criteria(active);
"""

print("1️⃣  Creating tables in Supabase...")
print()

try:
    # Execute SQL via Supabase REST API (using RPC)
    # Note: Direct SQL execution requires using the Supabase SQL Editor or API
    # For now, we'll use the Python client to create via schema

    print("⚠️  WICHTIG: Führe dieses SQL manuell im Supabase SQL Editor aus:")
    print()
    print("1. Gehe zu: https://app.supabase.com/project/lglvuiuwbrhiqvxcriwa/sql")
    print("2. Kopiere den SQL Code unten")
    print("3. Klicke 'RUN'")
    print()
    print("-" * 70)
    print(CREATE_TABLES_SQL)
    print("-" * 70)
    print()

    input("Drücke ENTER wenn du das SQL ausgeführt hast...")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print()
print("2️⃣  Füge 17 Sources ein...")
print()

# Data for 17 sources (from earlier)
SOURCES_DATA = [
    {"name": "Cologne Watch", "url": "https://www.colognewatch.de", "domain": "colognewatch.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://www.colognewatch.de/search?q={manufacturer}+{model}", "listing_selector": ".product-item", "title_selector": ".product-card__title", "price_selector": ".price-item", "link_selector": "a.product-item__link", "notes": "German luxury watch dealer"},
    {"name": "Watch Vice", "url": "https://watchvice.de", "domain": "watchvice.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://watchvice.de/search?q={manufacturer}+{model}", "listing_selector": ".product", "title_selector": "h3.product-title", "price_selector": ".product-price", "link_selector": "a.product-link", "notes": "Premium watch dealer"},
    {"name": "Watch.de", "url": "https://www.watch.de", "domain": "watch.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://www.watch.de/search?q={manufacturer}+{model}", "listing_selector": ".product-card", "title_selector": ".title", "price_selector": ".price", "link_selector": "a.link", "notes": "German watch retailer"},
    {"name": "Marks Uhren", "url": "https://marks-uhren.de", "domain": "marks-uhren.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://marks-uhren.de/search?q={manufacturer}+{model}", "listing_selector": ".product", "title_selector": ".name", "price_selector": ".price", "link_selector": "a", "notes": "Watch dealer Germany"},
    {"name": "Rothfuss Watches", "url": "https://rothfuss-watches.de", "domain": "rothfuss-watches.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://rothfuss-watches.de/search?q={manufacturer}+{model}", "listing_selector": ".item", "title_selector": ".title", "price_selector": ".price", "link_selector": "a", "notes": "German watch specialist"},
    {"name": "Karmann Watches", "url": "https://karmannwatches.de", "domain": "karmannwatches.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://karmannwatches.de/search?q={manufacturer}+{model}", "listing_selector": ".watch-item", "title_selector": ".watch-name", "price_selector": ".watch-price", "link_selector": "a", "notes": "Watch dealer Germany"},
    {"name": "Eupen Feine Uhren", "url": "https://eupenfeineuhren.de", "domain": "eupenfeineuhren.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://eupenfeineuhren.de/search?q={manufacturer}+{model}", "listing_selector": ".product", "title_selector": ".name", "price_selector": ".price", "link_selector": "a", "notes": "Fine watch dealer"},
    {"name": "G-Abriel", "url": "https://www.g-abriel.de", "domain": "g-abriel.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://www.g-abriel.de/search?q={manufacturer}+{model}", "listing_selector": ".watch", "title_selector": ".title", "price_selector": ".price", "link_selector": "a", "notes": "Watch specialist Germany"},
    {"name": "Bachmann & Scher", "url": "https://www.bachmann-scher.de", "domain": "bachmann-scher.de", "type": "Dealer", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://www.bachmann-scher.de/gebrauchte-luxusuhren-kaufen.html?q={manufacturer}+{model}", "listing_selector": ".watch-item", "title_selector": ".title", "price_selector": ".price", "link_selector": "a", "notes": "Used luxury watch dealer"},
    {"name": "Uhrforum.de", "url": "https://uhrforum.de/forums/angebote.11/", "domain": "uhrforum.de", "type": "Forum", "scraper_type": "Dynamic", "active": True, "requires_auth": True, "rate_limit_seconds": 3, "auth_username_env": "UHRFORUM_USERNAME", "auth_password_env": "UHRFORUM_PASSWORD", "search_url_template": "https://uhrforum.de/search/search?keywords={manufacturer}+{model}", "listing_selector": ".structItem", "title_selector": ".structItem-title", "price_selector": ".structItem-cell--meta", "link_selector": "a.structItem-title", "notes": "Major German watch forum"},
    {"name": "WatchLounge Forum", "url": "https://forum.watchlounge.com", "domain": "forum.watchlounge.com", "type": "Forum", "scraper_type": "Dynamic", "active": True, "requires_auth": True, "rate_limit_seconds": 3, "auth_username_env": "WATCHLOUNGE_USERNAME", "auth_password_env": "WATCHLOUNGE_PASSWORD", "search_url_template": "https://forum.watchlounge.com/search?q={manufacturer}+{model}", "listing_selector": ".topic", "title_selector": ".topic-title", "price_selector": ".topic-meta", "link_selector": "a", "notes": "Watch enthusiast forum"},
    {"name": "Uhr-Forum.org", "url": "https://uhr-forum.org/forum/", "domain": "uhr-forum.org", "type": "Forum", "scraper_type": "Dynamic", "active": True, "requires_auth": True, "rate_limit_seconds": 3, "auth_username_env": "UHR_FORUM_ORG_USERNAME", "auth_password_env": "UHR_FORUM_ORG_PASSWORD", "search_url_template": "https://uhr-forum.org/forum/search?q={manufacturer}+{model}", "listing_selector": ".post", "title_selector": ".post-title", "price_selector": ".post-meta", "link_selector": "a", "notes": "German watch forum"},
    {"name": "eBay.de", "url": "https://www.ebay.de", "domain": "ebay.de", "type": "Marketplace", "scraper_type": "Dynamic", "active": True, "requires_auth": False, "rate_limit_seconds": 3, "search_url_template": "https://www.ebay.de/sch/i.html?_nkw={manufacturer}+{model}", "listing_selector": ".s-item", "title_selector": ".s-item__title", "price_selector": ".s-item__price", "link_selector": "a.s-item__link", "notes": "eBay Germany"},
    {"name": "Kleinanzeigen.de", "url": "https://www.kleinanzeigen.de", "domain": "kleinanzeigen.de", "type": "Marketplace", "scraper_type": "Dynamic", "active": True, "requires_auth": False, "rate_limit_seconds": 3, "search_url_template": "https://www.kleinanzeigen.de/s-uhren/c172?q={manufacturer}+{model}", "listing_selector": "article.aditem", "title_selector": ".text-module-begin", "price_selector": ".aditem-main--middle--price", "link_selector": "a.ellipsis", "notes": "German classified ads"},
    {"name": "Chrono24", "url": "https://www.chrono24.de", "domain": "chrono24.de", "type": "Marketplace", "scraper_type": "Dynamic", "active": True, "requires_auth": False, "rate_limit_seconds": 3, "search_url_template": "https://www.chrono24.de/search/index.htm?query={manufacturer}+{model}", "listing_selector": "article.article-item", "title_selector": ".text-bold", "price_selector": ".article-item-price", "link_selector": "a.article-item-link", "notes": "Major watch marketplace"},
    {"name": "Chronext", "url": "https://www.chronext.de", "domain": "chronext.de", "type": "Marketplace", "scraper_type": "Dynamic", "active": True, "requires_auth": False, "rate_limit_seconds": 3, "search_url_template": "https://www.chronext.de/search?q={manufacturer}+{model}", "listing_selector": ".product-tile", "title_selector": ".product-name", "price_selector": ".product-price", "link_selector": "a.product-link", "notes": "Premium watch marketplace"},
    {"name": "Uhrinstinkt", "url": "https://www.uhrinstinkt.de", "domain": "uhrinstinkt.de", "type": "Marketplace", "scraper_type": "Static", "active": True, "requires_auth": False, "rate_limit_seconds": 2, "search_url_template": "https://www.uhrinstinkt.de/search?q={manufacturer}+{model}", "listing_selector": ".watch", "title_selector": ".watch-title", "price_selector": ".watch-price", "link_selector": "a", "notes": "German watch marketplace"},
]

try:
    for source in SOURCES_DATA:
        result = supabase.table('watch_sources').insert(source).execute()
        print(f"  ✓ {source['name']}")

    print()
    print("=" * 70)
    print("🎉 Setup Complete!")
    print("=" * 70)
    print()
    print("✅ 4 Tables created")
    print("✅ 17 Sources populated")
    print()
    print("Next: View your data at:")
    print("https://app.supabase.com/project/lglvuiuwbrhiqvxcriwa/editor")

except Exception as e:
    print(f"❌ Error inserting sources: {e}")
    print("Make sure you ran the SQL script first!")

