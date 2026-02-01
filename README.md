# Watch Service

Automated luxury watch monitoring service that searches 15+ grey market sources hourly, extracts data using OpenAI, stores findings in Notion, tracks availability, and sends email notifications.

## Overview

**Status:** Production Ready ✅
**Tech Stack:** Python 3.12, Notion API, OpenAI GPT-4o-mini, BeautifulSoup, Selenium
**Deployment:** Hostinger VPS (72.62.148.205) via cronjobs
**Cost:** ~€20-30/month (OpenAI API)

## Features

- 🔍 **Hourly Searches** - Monitors 15+ sources every hour
- 🤖 **AI-Powered Extraction** - Uses GPT-4o-mini for structured data extraction
- 🗄️ **Centralized Storage** - All findings stored in Notion databases
- 📧 **Email Notifications** - Instant alerts for new matches
- 🌍 **Country Filtering** - Strict filtering by allowed countries
- 🔄 **Availability Tracking** - Auto-marks sold listings
- 🚀 **Dynamic Source Management** - Add/remove sources via Notion (no code changes!)
- 🎯 **Generic Scraper** - 80% of sources work without custom code

## Architecture

### The Game Changer: Notion-Configured Sources

Unlike traditional scrapers, Watch Service stores **all source configurations in Notion**:

- **No Code Changes Needed** - Add new sources via Notion UI
- **Update CSS Selectors** - Change selectors without deployment
- **Track Source Health** - Monitor error rates per source
- **Enable/Disable Sources** - Toggle Active checkbox
- **Custom Scraper Fallback** - Complex sources can use custom Python files

### File Structure

```
Watch_Service/
├── config/
├── core/
│   ├── notion_client.py       # Notion API wrapper
│   ├── openai_extractor.py    # OpenAI data extraction
│   └── email_sender.py        # Email notifications
├── scrapers/
│   ├── base_scraper.py        # Abstract base class
│   ├── static_scraper.py      # BeautifulSoup engine
│   ├── dynamic_scraper.py     # Selenium engine
│   └── generic_scraper.py     # 🚀 GAME CHANGER - Notion-configured
├── sources/custom/            # Custom scrapers (only if needed)
├── utils/
│   ├── logger.py              # Emoji logging
│   ├── rate_limiter.py        # Respectful scraping
│   └── text_utils.py          # Text processing
├── watch_searcher.py          # Main hourly search
├── availability_checker.py    # Availability tracking
├── setup_notion_databases.py  # One-time Notion setup
├── test_complete_system.py    # Safe system test
├── requirements.txt
├── .env.example
└── .gitignore
```

## Notion Database Structure

### 1. Sources (Configuration DB) 🚀

**Purpose:** Dynamic source management - no code changes needed!

**Key Properties:**
- `Name` - Source display name
- `URL` - Base URL
- `Type` - Dealer/Forum/Marketplace
- `Scraper_Type` - Static/Dynamic
- `Active` - Enable/disable source
- `Search_URL_Template` - URL pattern with {manufacturer} {model}
- `Listing_Selector` - CSS selector for listings
- `Title_Selector`, `Price_Selector`, `Link_Selector` - Data selectors
- `Rate_Limit_Seconds` - Delay between requests
- `Last_Successful_Scrape`, `Error_Count` - Health tracking

**Pre-Configured Sources (17):**
- 9 Dealers (Cologne Watch, Watch Vice, etc.)
- 3 Forums (Uhrforum.de, WatchLounge, etc.)
- 5 Marketplaces (eBay, Chrono24, Kleinanzeigen, etc.)

### 2. Watch_Search_Criteria (Input)

**What to search for:**
- `Manufacturer` (REQUIRED)
- `Model` (REQUIRED)
- `Reference_Number` (optional)
- `Year` (optional)
- `Allowed_Countries` - Germany, Austria, Switzerland, etc.
- `Active` - Enable/disable search

### 3. Watch_Listings (Output)

**Found watches:**
- Date, Manufacturer, Model, Reference, Year
- Condition, Price, Currency, Location, Country
- Link, Seller Name, Source
- `Availability` - Available/Sold
- `Sold_At` - Timestamp when marked sold
- `URL_Hash` - For duplicate detection

### 4. Sync_History (Logging)

**Run statistics:**
- Date, Status, Duration
- Sources checked/failed
- Listings found/saved
- Duplicates skipped

## Quick Start

### 1. Setup Python Environment

```bash
cd Watch_Service
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

**Required credentials (5 minutes):**
- `NOTION_API_KEY` - Create at https://www.notion.so/my-integrations
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `SMTP_USER` / `SMTP_PASSWORD` - Gmail App Password for notifications
- `RECIPIENT_EMAIL` - Where to send notifications

### 3. Setup Notion Databases

```bash
python3 setup_notion_databases.py
```

**What this does:**
1. Creates 4 Notion databases (Sources, Criteria, Listings, History)
2. Populates Sources DB with 17 pre-configured sources
3. Updates .env with database IDs
4. Takes ~2 minutes

**You'll need:**
- Notion API Key
- Parent Page ID (where to create databases)

### 4. Add Search Criteria

In Notion, open **Watch_Search_Criteria** database and add entries:

**Example:**
- `Manufacturer`: Rolex
- `Model`: Submariner
- `Allowed_Countries`: Germany, Austria, Switzerland
- `Active`: ✓

### 5. Test System

```bash
python3 test_complete_system.py
```

**Safe test - only uses 1 source:**
- ✅ Tests Notion connection
- ✅ Tests scraper
- ✅ Tests OpenAI extraction
- ✅ Tests duplicate detection
- ✅ Validates email config

### 6. Manual Production Test

```bash
python3 watch_searcher.py
```

**Searches ALL 17 sources:**
- Check logs: `tail -f watch_service.log`
- Verify listings in Notion
- Check email notifications

### 7. Deploy to VPS (Hostinger)

```bash
# SSH to VPS
ssh root@72.62.148.205

# Clone and setup
cd ~
git clone <repo-url> Watch_Service
cd Watch_Service
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Configure
nano .env  # Add all credentials

# Install Chrome for Selenium
apt-get update
apt-get install -y chromium-browser chromium-chromedriver

# Test manually
python3 watch_searcher.py

# Add cronjobs
crontab -e
```

**Add to crontab:**
```bash
# Watch Service - Hourly Search
0 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 watch_searcher.py >> watch_service.log 2>&1

# Watch Service - Availability Check (30 min offset)
30 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 availability_checker.py >> availability_check.log 2>&1
```

**Monitor logs:**
```bash
tail -f watch_service.log
tail -f availability_check.log
```

## How It Works

### Main Search Flow (watch_searcher.py)

```
1. Load active sources from Notion Sources DB
2. Load search criteria from Notion
3. For each source:
   a. Initialize GenericScraper with Notion config
   b. For each search criteria:
      - Build search URL from template
      - Scrape page using CSS selectors
      - Extract structured data with OpenAI
      - Filter by allowed countries (strict)
      - Check duplicates via URL hash
      - Save new listings to Notion
   c. Update source stats (success/errors)
4. Send email if new listings found
5. Log run statistics to Sync_History
```

### Generic Scraper Magic ✨

```python
# Source config from Notion:
{
  "Name": "Cologne Watch",
  "Search_URL_Template": "https://colognewatch.de/search?q={manufacturer}+{model}",
  "Listing_Selector": ".product-item",
  "Title_Selector": ".product-title",
  "Price_Selector": ".price",
  "Link_Selector": "a.product-link"
}

# GenericScraper automatically:
1. Builds search URL by replacing {manufacturer} and {model}
2. Fetches page (static or dynamic based on Scraper_Type)
3. Extracts listings using CSS selectors
4. Returns structured data

# NO CUSTOM CODE NEEDED! 🎉
```

### Adding New Sources (No Code!)

1. Open Notion **Sources** database
2. Click "New"
3. Fill in:
   - Name, URL, Domain, Type, Scraper_Type
   - Search_URL_Template with {manufacturer} {model} placeholders
   - CSS selectors (inspect site's HTML)
   - Rate_Limit_Seconds
   - Active ✓
4. Done! Next search run will include this source

**Research CSS Selectors:**
```bash
1. Visit source website
2. Open browser DevTools (F12)
3. Find repeating listing element
4. Copy CSS selector
5. Test in DevTools console: document.querySelectorAll('.selector')
6. Add to Notion Sources DB
```

## Email Notifications

When new watches are found, you receive:

**Subject:** 🎯 X neue Uhren gefunden!

**Content:**
- Summary with count
- Each watch card with:
  - Manufacturer + Model + Reference
  - Price in bold
  - Condition, Location, Source
  - "Angebot ansehen →" button with direct link

**Sample:**
```
🎯 Watch Service
3 neue Uhren gefunden!

Datum: 01.02.2026 14:30 Uhr
───────────────────────────

Rolex Submariner (116610LN)
€ 8.999,00
Zustand: Sehr Gut
Standort: München, Germany
Quelle: Cologne Watch
[Angebot ansehen →]

...
```

## Monitoring & Maintenance

### Check System Health

```bash
# View recent logs
tail -f watch_service.log

# Check cronjob execution
grep CRON /var/log/syslog | tail -20

# Check Notion Sync_History
# Open Sync_History DB in Notion - shows all runs

# Check Sources error counts
# Open Sources DB - sort by Error_Count desc
```

### Update Source Configurations

**In Notion (no deployment needed!):**
- Update CSS selectors if site HTML changes
- Change rate limits if getting blocked
- Disable failing sources (Active = unchecked)
- Add new sources

**Track Source Health:**
- `Last_Successful_Scrape` - When last worked
- `Error_Count` - Consecutive failures (auto-resets on success)
- `Notes` - Error messages

### Cost Monitoring

**OpenAI Usage:**
- Monitor at https://platform.openai.com/usage
- Set usage limit: $50/month
- Expected: €20-30/month (~108M tokens)

**Cost breakdown:**
- 17 sources × 10 listings/source/hour × 24 hours = 4,080 listings/day
- ~1000 tokens/listing = 4M tokens/day = 120M tokens/month
- GPT-4o-mini: $0.15/1M input + $0.60/1M output
- Estimated: $18-25/month

## Troubleshooting

### "No active sources found"
**Solution:** Run `python3 setup_notion_databases.py`

### "No search criteria found"
**Solution:** Add at least one entry in Notion Watch_Search_Criteria database

### "OpenAI extraction failed"
**Causes:**
- Low confidence score (< 0.5)
- Invalid HTML structure
- API error

**Solution:** Check logs, increase confidence threshold, verify OpenAI API key

### "Email not sent"
**Causes:**
- SMTP credentials not configured
- Gmail blocking "less secure apps"

**Solution:**
- Use Gmail App Password (not account password)
- Enable 2-factor auth, then create App Password

### "Source always fails"
**Causes:**
- Site HTML changed (CSS selectors outdated)
- IP banned (rate limit too low)
- Site requires authentication

**Solutions:**
1. Update CSS selectors in Notion Sources DB
2. Increase Rate_Limit_Seconds
3. Add authentication credentials to .env
4. Disable source temporarily (Active = unchecked)

### "Getting IP banned"
**Solutions:**
- Increase rate limits (3-5 seconds)
- Use VPN/proxy (add to scrapers if needed)
- Reduce Active sources

### "Selenium fails on VPS"
**Causes:**
- Chrome not installed
- Headless mode issues

**Solutions:**
```bash
# Install Chrome
apt-get update
apt-get install -y chromium-browser chromium-chromedriver

# Verify
chromium-browser --version
chromedriver --version

# Test Selenium
python3 -c "from selenium import webdriver; webdriver.Chrome()"
```

## Advanced Usage

### Custom Scrapers for Complex Sites

If GenericScraper doesn't work (login flows, CAPTCHA, complex JS):

1. Create custom scraper in `sources/custom/`:

```python
# sources/custom/chrono24_custom.py
from scrapers.base_scraper import BaseScraper

class Chrono24Custom(BaseScraper):
    def search(self, criteria):
        # Custom login logic
        # Custom search logic
        # Return listings
        pass

    def check_availability(self, url):
        # Custom availability check
        pass
```

2. Update Notion Sources DB:
   - Set `Custom_Scraper` = `chrono24_custom.py`
   - GenericScraper will automatically load your custom class

### Parallel Execution (Future Enhancement)

For faster execution, run sources in parallel:

```python
# In watch_searcher.py (future)
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(self._search_source, sources)
```

### Custom Filters (Future Enhancement)

Add custom filtering logic:

```python
# In openai_extractor.py
def filter_by_price_range(self, extracted, min_price, max_price):
    price = extracted.get('price', 0)
    return min_price <= price <= max_price
```

## Related Projects

This project follows patterns from:
- **Blackfire_automation** - Python + Notion + cronjobs + VPS
- **Passive Income** - OpenAI integration + duplicate detection

See `/Users/robin/Documents/4_AI/CLAUDE.md` for workspace overview.

## Security

- **Never commit credentials** - use `.env` (git-ignored)
- Store credentials in `/Users/robin/Documents/4_AI/Passwords/`
- Use 1Password CLI for credential management
- Respect robots.txt and rate limits
- Use dedicated accounts for forums (not personal)

## Legal Considerations

- Web scraping may violate some sites' Terms of Service
- Use official APIs where available (eBay, Chrono24)
- Respect rate limits to avoid IP bans
- Consider ethical implications
- For educational/personal use only

## Support

**Author:** Robin Seckler (rseckler@gmail.com)
**VPS:** Hostinger (72.62.148.205)
**Deployment:** Manual or git push + SSH

## License

Private project - not for commercial use

---

**Status:** Production Ready ✅
**Last Updated:** 2026-02-01
**Version:** 1.0.0
