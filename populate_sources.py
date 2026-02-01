"""
Populate Supabase watch_sources table with 17 pre-configured sources
Run this after creating tables via SQL
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
print("🚀 Watch Service - Populate Sources")
print("=" * 70)
print()

# Data for 17 sources
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
    count = 0
    for source in SOURCES_DATA:
        result = supabase.table('watch_sources').insert(source).execute()
        print(f"  ✓ {source['name']}")
        count += 1

    print()
    print("=" * 70)
    print("🎉 Sources Populated Successfully!")
    print("=" * 70)
    print()
    print(f"✅ {count} sources added to watch_sources table")
    print()
    print("Next: View your data at:")
    print("https://app.supabase.com/project/lglvuiuwbrhiqvxcriwa/editor")

except Exception as e:
    print(f"❌ Error inserting sources: {e}")
    print()
    print("💡 This might happen if sources were already inserted.")
    print("   Check your Supabase table at:")
    print("   https://app.supabase.com/project/lglvuiuwbrhiqvxcriwa/editor")
