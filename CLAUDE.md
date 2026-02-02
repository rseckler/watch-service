# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Watch_Service** is an automated luxury watch monitoring service that tracks availability of specific watch models across grey market sources (dealers, marketplaces). The service runs hourly searches, stores findings in PostgreSQL database, and provides a Next.js web interface for browsing results.

**Status:** ✅ **PRODUCTION** - Deployed and running on VPS

**Last Updated:** 2026-02-02

## Current System Status

### 🚀 Active Components

1. **Backend Scrapers (Python)** - Running hourly via cronjob on VPS
   - ✅ Cologne Watch (Static scraper)
   - ✅ Kleinanzeigen.de (Selenium + keyword matching)
   - ✅ Rothfuss Watches (Selenium scraper)
   - ✅ Watch.de (Selenium + Search + Overview pages)

2. **Web Interface (Next.js)** - Running on PM2
   - URL: http://72.62.148.205:3001
   - Pages: Dashboard, Listings (with sorting), Criteria, Sources, Logs
   - Features: Filter, search, sort by price/date/source/manufacturer/model

3. **Database (PostgreSQL/Neon)**
   - Host: ep-falling-frost-ah4cx5b4-pooler.c-3.us-east-1.aws.neon.tech
   - 51+ GMT-Master II watches from 4 sources

### 📊 Latest Statistics

**Search Results (as of 2026-02-02):**
- Cologne Watch: 7 GMT-Master II listings
- Kleinanzeigen: 27 GMT-Master II listings
- Rothfuss Watches: Active (no current GMT-Master II)
- Watch.de: 17 GMT-Master II listings

**Total:** 51+ GMT-Master II watches tracked

### 🆕 Recent Changes (2026-02-02)

1. **Watch.de Scraper Fixed:**
   - Changed from `/rolex` to `/germany/rolex.html` (correct URL)
   - Added search functionality: `/germany/search.html?query={query}`
   - Implemented "Zeig mehr" button clicking for pagination
   - Now finds 17 GMT-Master II watches (was 0)

2. **Sorting Functionality Added to Listings Page:**
   - Sort by: Price (asc/desc), Date (newest/oldest), Source (A-Z), Manufacturer (A-Z), Model (A-Z)
   - Client-side sorting for fast performance
   - Integrated with existing filters

3. **Web App Deployed on VPS:**
   - Location: `/root/Watch_Service_Web/`
   - Running on port 3001 with PM2
   - Auto-restart on reboot configured

## Architecture

### Tech Stack

**Backend (Python 3.12):**
- Selenium (Chromium snap) for JavaScript-rendered sites
- BeautifulSoup + lxml for HTML parsing
- OpenAI GPT-4o-mini for data extraction (dealers only)
- PostgreSQL (psycopg2) for database
- URL hashing (SHA256) for duplicate detection

**Frontend (Next.js 15):**
- React 19 + TypeScript
- Tailwind CSS
- React Query for data fetching
- Deployed with PM2

**Database:**
- PostgreSQL on Neon (Vercel Postgres migration)
- Tables: watch_listings, search_criteria, sources, sync_history

### Scraping Strategies

**1. Cologne Watch (Static):**
- BeautifulSoup parser
- CSS selectors: `.product-item`, `.price`
- OpenAI extraction for structured data

**2. Kleinanzeigen (Keyword Matching):**
- Selenium for JavaScript rendering
- Keyword list: gmt, master, pepsi, batman, batgirl, coke, rootbeer, sprite, blnr, blro
- NO OpenAI (to avoid hallucinations)
- German price format: "13.750 € VB" → 13750

**3. Rothfuss Watches (Selenium):**
- Shopify store with Cloudflare challenge
- Wait time: 10 seconds for Cloudflare
- Fallback selector: `[class*="product"]`

**4. Watch.de (Dual Strategy):**
- Search: `/germany/search.html?query=Rolex+GMT-Master+II`
- Overview: `/germany/rolex.html`
- "Zeig mehr" button clicking for pagination
- Combines both sources, deduplicates by URL hash

### OpenAI Integration

**Model:** GPT-4o-mini
**Confidence Threshold:** 0.5
**Usage:** Dealers only (not Kleinanzeigen)

**Key Changes to Prevent Hallucination:**
- Removed search criteria from prompt (was causing bias)
- Added confidence threshold rejection
- Changed system prompt to "ONLY extract information that is explicitly present"

**Cost:** ~€20-30/month (within budget)

## File Structure

```
Watch_Service/
├── backend/                    # Python scrapers (on VPS)
│   ├── core/
│   │   ├── database.py        # PostgreSQL client
│   │   └── openai_extractor.py # GPT-4o-mini extraction
│   ├── scrapers/
│   │   ├── base_scraper.py
│   │   ├── selenium_scraper.py
│   │   ├── cologne_watch_scraper.py
│   │   ├── kleinanzeigen_scraper.py
│   │   ├── rothfuss_watches_selenium.py
│   │   └── watch_de_selenium.py
│   ├── watch_searcher.py      # Main orchestration script
│   └── .env                   # Database credentials
├── app/                       # Next.js pages
│   ├── listings/
│   │   └── page.tsx          # Listings page with sorting
│   ├── criteria/
│   ├── sources/
│   └── logs/
├── components/                # React components
├── lib/
│   └── db.ts                 # Database client (frontend)
├── package.json
└── .env.local                # Database credentials (web)
```

## Deployment

### VPS Configuration

**Server:** 72.62.148.205 (Hostinger Ubuntu)
**Node.js:** 20.20.0
**Python:** 3.12
**Chromium:** 144.0.7559.96 (snap)

### Backend Deployment

**Location:** `/root/Watch_Service/backend/`

**Cronjob (Hourly Search):**
```bash
0 * * * * cd /root/Watch_Service/backend && source venv/bin/activate && python3 watch_searcher.py >> /root/Watch_Service/watch_service.log 2>&1
```

**View Logs:**
```bash
tail -f /root/Watch_Service/watch_service.log
```

### Web App Deployment

**Location:** `/root/Watch_Service_Web/`

**PM2 Configuration:**
```bash
# Status
pm2 status

# Logs
pm2 logs watch-service-web

# Restart
pm2 restart watch-service-web

# Saved config
pm2 save
```

**Environment Variables (.env.local):**
```bash
POSTGRES_URL="postgresql://neondb_owner:npg_qI6TeuyY2gwM@ep-falling-frost-ah4cx5b4-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
POSTGRES_USER="neondb_owner"
POSTGRES_HOST="ep-falling-frost-ah4cx5b4-pooler.c-3.us-east-1.aws.neon.tech"
POSTGRES_PASSWORD="npg_qI6TeuyY2gwM"
POSTGRES_DATABASE="neondb"
```

## Development Commands

### Backend (Python)

```bash
cd backend
source venv/bin/activate

# Run manual search
python3 watch_searcher.py

# Test specific scraper
python3 -c "from scrapers.watch_de_selenium import WatchDeSeleniumScraper; s = WatchDeSeleniumScraper(); print(s.search({'manufacturer': 'Rolex', 'model': 'GMT-Master II'}))"

# Check database
python3 -c "from core.database import Database; db = Database(); print(db.execute_query('SELECT COUNT(*) FROM watch_listings'))"
```

### Frontend (Next.js)

```bash
# Local development
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npm run type-check
```

## Web Interface Access

### URLs

- **Production:** http://72.62.148.205:3001
- **Dashboard:** http://72.62.148.205:3001/
- **Listings (with sorting):** http://72.62.148.205:3001/listings
- **Search Criteria:** http://72.62.148.205:3001/criteria
- **Sources:** http://72.62.148.205:3001/sources
- **Logs:** http://72.62.148.205:3001/logs

### Listings Page Features

1. **Search:** Filter by manufacturer, model, reference number
2. **Filter by Source:** Dropdown with all sources
3. **Filter by Availability:** Available, Sold, Unknown
4. **Sort Options:**
   - Preis aufsteigend/absteigend
   - Neueste/Älteste zuerst
   - Hersteller A-Z / Z-A
   - Modell A-Z / Z-A
   - Quelle A-Z / Z-A

## Database Schema

### watch_listings

```sql
CREATE TABLE watch_listings (
    id SERIAL PRIMARY KEY,
    date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    manufacturer VARCHAR(100),
    model VARCHAR(200),
    reference_number VARCHAR(100),
    year INTEGER,
    condition VARCHAR(50),
    price DECIMAL(10,2),
    currency VARCHAR(10),
    location VARCHAR(200),
    country VARCHAR(100),
    link TEXT UNIQUE,
    seller_name VARCHAR(200),
    image_url TEXT,
    source VARCHAR(100),
    source_type VARCHAR(50),
    availability VARCHAR(20) DEFAULT 'Available',
    sold_at TIMESTAMP,
    last_checked TIMESTAMP,
    url_hash VARCHAR(64) UNIQUE,
    raw_data JSONB
);
```

### search_criteria

```sql
CREATE TABLE search_criteria (
    id SERIAL PRIMARY KEY,
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(200) NOT NULL,
    reference_number VARCHAR(100),
    year INTEGER,
    allowed_countries TEXT[],
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Known Issues & Solutions

### Issue 1: Watch.de Returns No GMT-Master II
**Cause:** Using wrong URL (`/rolex` instead of `/germany/rolex.html`)
**Solution:** ✅ Fixed - Now uses correct URL + search + pagination

### Issue 2: Kleinanzeigen False Positives
**Cause:** OpenAI hallucination due to search criteria in prompt
**Solution:** ✅ Fixed - Switched to keyword matching, no OpenAI

### Issue 3: Port 3000 Already in Use
**Cause:** Blackfire service using port 3000
**Solution:** ✅ Fixed - Watch service runs on port 3001

### Issue 4: Sequential Selenium Initialization
**Cause:** Multiple Selenium instances cause "unable to connect to renderer" errors
**Solution:** ✅ Implemented - Scrapers initialize sequentially with 2-second delays

## Cost Analysis

### Monthly Costs

- **OpenAI API (GPT-4o-mini):** €20-30/month
  - ~136 listings/run × 24 runs/day × 30 days = 97,920 API calls/month
  - Average 2000 tokens/call = ~200M tokens/month
  - Cost: $0.15/1M input + $0.60/1M output tokens ≈ €25/month

- **VPS:** €0 (already paid via Hostinger)
- **Database (Neon):** €0 (free tier sufficient)

**Total: €20-30/month** ✅ Within budget

## Future Enhancements

### Potential Improvements
- [ ] Add email notifications for new listings
- [ ] Implement availability checker (mark sold listings)
- [ ] Add more sources (watchvice.de, marks-uhren.de, etc.)
- [ ] Set up nginx reverse proxy for cleaner URLs
- [ ] Add authentication to web interface
- [ ] Implement price history tracking
- [ ] Add mobile-responsive design improvements

### Monitoring
- [ ] Set up uptime monitoring for web app
- [ ] Add error alerting for scraper failures
- [ ] Track OpenAI API usage to prevent overages

## Troubleshooting

### Backend Not Running
```bash
ssh root@72.62.148.205
cd /root/Watch_Service/backend
source venv/bin/activate
python3 watch_searcher.py  # Test manually
crontab -l  # Check cronjob is active
```

### Web App Not Accessible
```bash
ssh root@72.62.148.205
pm2 status  # Check if watch-service-web is online
pm2 logs watch-service-web  # Check for errors
pm2 restart watch-service-web  # Restart if needed
```

### Database Connection Issues
```bash
# Test database connection
psql "postgresql://neondb_owner:npg_qI6TeuyY2gwM@ep-falling-frost-ah4cx5b4-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Selenium Errors
```bash
# Check Chromium is installed
snap list chromium

# Test Selenium manually
cd /root/Watch_Service/backend && source venv/bin/activate
python3 -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service; service = Service('/snap/bin/chromium.chromedriver'); driver = webdriver.Chrome(service=service); driver.get('https://www.google.com'); print('OK'); driver.quit()"
```

## Git Repository

**Remote:** https://github.com/rseckler/watch-service.git

**Branches:**
- `main` - Production branch (deployed on VPS)

**Recent Commits:**
- Add sorting functionality to listings page (2026-02-02)
- Fix Watch.de scraper with correct URLs and pagination (2026-02-02)
- Implement keyword matching for Kleinanzeigen (2026-02-02)

## Related Projects

This project follows patterns from:
- **Blackfire_automation:** Python + PostgreSQL + cronjobs + VPS deployment
- **Passive Income:** OpenAI integration + duplicate detection
- **Blackfire_service:** Next.js + PostgreSQL + Vercel deployment patterns

See `/Users/robin/Documents/4_AI/CLAUDE.md` for workspace overview and shared infrastructure.

## Contact & Support

**Author:** Robin Seckler
**Email:** rseckler@gmail.com
**VPS:** Hostinger support
