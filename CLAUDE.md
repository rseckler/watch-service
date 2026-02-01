# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Watch_Service** is an automated luxury watch monitoring service that tracks availability of specific watch models across grey market sources (forums, dealers, marketplaces). The service runs hourly searches, stores findings in Notion, and tracks when listings become unavailable (sold).

**Status:** Planning phase - implementation pending

**Planning Document:** `Uhren_Service.md` contains complete requirements and target sources

## Project Goals

- **Hourly Monitoring:** Search for specific watch models across 15+ grey market sources
- **Availability Tracking:** Mark when previously found watches are sold with timestamp
- **Centralized Storage:** Store all findings in Notion database
- **Speed:** Enable fast response to new listings to secure best prices
- **AI-Enhanced Matching:** Use OpenAI to improve search accuracy and data extraction

## Target Sources

### Watch Forums (require authentication)
- uhrforum.de (login: robin@seckler.de)
- forum.watchlounge.com
- uhr-forum.org

### Grey Market Dealers (public websites)
- colognewatch.de
- watchvice.de
- watch.de
- marks-uhren.de
- rothfuss-watches.de
- karmannwatches.de
- eupenfeineuhren.de
- g-abriel.de
- bachmann-scher.de

### Marketplaces (require authentication)
- Ebay.de (login: smc_001)
- Kleinanzeigen.de (login: seckler@seckler.de)
- Chrono24.de
- chronext.de
- uhrinstinkt.de

**Note:** Credentials should be managed via `/Users/robin/Documents/4_AI/Passwords/` directory structure (see root CLAUDE.md).

## Notion Database Structure

### Search Criteria DB (Input)
Stores user-defined watch models to search for:
- Uhrenhersteller (Manufacturer)
- Uhrenmodell (Model)
- Referenznummer (Reference Number)
- Jahr (Year)
- Länder (Allowed Countries)

**Note:** Manufacturer and Model are mandatory fields.

### Listings DB (Output)
Stores found watches with extracted data:
- Datum des Eintrags (Date Found)
- Hersteller (Manufacturer)
- Modell (Model)
- Referenznummer (Reference Number)
- Herstellungsjahr (Manufacturing Year)
- Zustand (Condition)
- Preis (Price)
- Standort (Location)
- Link (Direct URL to listing)
- Anbieter Name (Seller Name)
- Anbieter URL (Seller Website)
- Verfügbarkeit (Availability: yes/no)
- Verkauft am (Sold At: timestamp)

## Architecture Considerations

### Recommended Tech Stack
Based on existing projects in workspace (`/Users/robin/Documents/4_AI/`):
- **Python 3.12** (consistent with Blackfire_automation, Passive Income)
- **Libraries:** requests, beautifulsoup4, selenium (for JS-heavy sites), notion-client, openai, python-dotenv
- **Deployment:** Hostinger VPS (72.62.148.205) via cronjob (hourly)
- **Environment:** Use virtual environment (venv)

### Web Scraping Strategy
Different sources require different approaches:
- **Static Sites:** requests + BeautifulSoup
- **JS-Rendered Sites:** Selenium/Playwright
- **Forums with Auth:** Session management + cookie persistence
- **APIs:** Direct API calls where available (Chrono24, eBay)

### OpenAI Integration
Use GPT-4o/GPT-4o-mini for:
- Extracting structured data from unstructured listings
- Matching found watches to search criteria (fuzzy matching)
- Normalizing manufacturer/model names
- Determining condition from German descriptions

### Duplicate Detection
Prevent re-adding same listing:
- Track unique identifier (URL hash or listing ID)
- Compare key fields (price, seller, reference number)
- Use OpenAI for semantic similarity if needed

### Availability Checking
On each hourly run:
1. Fetch all listings with `Verfügbarkeit: yes`
2. Check if URL still accessible and listing still active
3. If unavailable → set `Verfügbarkeit: no` and `Verkauft am: <timestamp>`

## Development Commands

Once implemented, typical workflow:

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Notion API key, OpenAI key, credentials

# Run manual search
python3 watch_searcher.py

# Test single source
python3 test_source.py --source uhrforum

# Check availability updates
python3 availability_checker.py

# View logs
tail -f watch_service.log
```

## Deployment (VPS)

Deploy to existing Hostinger VPS (72.62.148.205):

```bash
# SSH to VPS
ssh root@72.62.148.205

# Clone repository
cd ~
git clone <repo-url> Watch_Service
cd Watch_Service
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Configure environment
nano .env

# Test manually
python3 watch_searcher.py

# Add to crontab (hourly)
crontab -e
# Add: 0 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 watch_searcher.py >> watch_service.log 2>&1
```

## Cost Considerations

Estimated monthly costs:
- **OpenAI API:** ~$5-15/month (depends on listing volume)
- **VPS:** $0 (already paid via Hostinger)
- **Notion API:** $0 (free tier sufficient)

Optimization:
- Use GPT-4o-mini for data extraction (cheaper)
- Cache responses for identical listings
- Rate limit API calls to stay within free tiers where possible

## Related Projects

This project follows patterns from:
- **Blackfire_automation:** Python + Notion + cronjobs + VPS deployment
- **Passive Income:** OpenAI integration + duplicate detection + Notion storage

See `/Users/robin/Documents/4_AI/CLAUDE.md` for workspace overview and shared infrastructure.

## Security Notes

- **Never commit credentials** - use `.env` files (add to `.gitignore`)
- Store credentials centrally in `/Users/robin/Documents/4_AI/Passwords/`
- Use 1Password CLI for credential management (see Passwords/CREDENTIALS-SETUP.md)
- Forum/marketplace logins may require CAPTCHA handling
- Respect robots.txt and rate limits to avoid IP bans

## Implementation Priority

Suggested development order:
1. Setup Notion databases (Search Criteria + Listings)
2. Implement single source scraper (start with easiest: colognewatch.de)
3. Add OpenAI extraction layer
4. Implement duplicate detection
5. Add availability checker
6. Expand to all sources incrementally
7. Deploy to VPS with hourly cronjob
8. Add error handling and notifications

## Legal Considerations

Web scraping may violate terms of service on some platforms. Review each source's ToS and consider:
- Using official APIs where available (eBay, Chrono24)
- Implementing rate limiting
- Respecting robots.txt
- Adding user-agent headers
- Considering ethical implications of automated purchases
