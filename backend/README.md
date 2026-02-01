# Watch Service Backend

Python backend for scraping luxury watch listings from grey market sources.

## Architecture

```
backend/
├── core/                    # Core modules
│   ├── database.py         # PostgreSQL connection
│   └── openai_extractor.py # OpenAI data extraction
├── scrapers/                # Source scrapers
│   ├── base_scraper.py     # Base class
│   └── cologne_watch_scraper.py  # Example scraper
├── utils/                   # Utilities
├── tests/                   # Tests
├── watch_searcher.py        # Main script
└── requirements.txt         # Dependencies
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
nano .env
```

Required environment variables:
- `POSTGRES_URL_NON_POOLING` - Database connection string
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)

### 4. Test Connection

```bash
python3 -c "from core.database import Database; db = Database(); print('✓ Database connected')"
```

## Usage

### Run Manual Search

```bash
python3 watch_searcher.py
```

This will:
1. Load active search criteria from database
2. Search all configured sources
3. Extract structured data with OpenAI
4. Save new listings to database
5. Log results to sync_history

### Output

Logs are written to:
- Console (stdout)
- `watch_service.log` file

Example output:
```
2026-02-01 20:00:00 - INFO - 🔍 Watch Searcher Starting...
2026-02-01 20:00:01 - INFO - ✓ Database connected successfully
2026-02-01 20:00:02 - INFO - ✓ OpenAI client initialized (model: gpt-4o-mini)
2026-02-01 20:00:02 - INFO - ✓ Initialized 1 scrapers
2026-02-01 20:00:03 - INFO - 📋 Found 1 active search criteria
2026-02-01 20:00:03 - INFO - 🎯 Searching for: Rolex GMT-Master II
2026-02-01 20:00:05 - INFO - 🔍 Searching Cologne Watch for: Rolex GMT-Master II
2026-02-01 20:00:07 - INFO - ✓ Found 3 listings on Cologne Watch
2026-02-01 20:00:10 - INFO - ✓ Extracted data: Rolex GMT-Master II - 15990 EUR
2026-02-01 20:00:11 - INFO - ✓ Created listing: Rolex GMT-Master II
2026-02-01 20:00:12 - INFO - 📊 SEARCH SUMMARY
2026-02-01 20:00:12 - INFO - Sources checked:     1
2026-02-01 20:00:12 - INFO - Listings saved:      1
```

## Adding New Scrapers

### 1. Create Scraper Class

```python
# scrapers/my_source_scraper.py
from .base_scraper import BaseScraper

class MySourceScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="My Source",
            source_url="https://example.com",
            rate_limit=2  # seconds between requests
        )

    def search(self, search_criteria):
        # Build search URL
        search_url = f"{self.source_url}/search?q=..."

        # Fetch and parse
        soup = self.fetch_page(search_url)

        # Extract listings
        listings = []
        for item in soup.select('.product'):
            listings.append({
                'title': item.select_one('.title').text,
                'link': item.select_one('a')['href'],
                'raw_html': str(item),
                'source_name': self.source_name,
                'source_type': 'Dealer',
                'url_hash': self.generate_url_hash(link)
            })

        return listings
```

### 2. Register Scraper

Add to `watch_searcher.py`:
```python
from scrapers.my_source_scraper import MySourceScraper

def _initialize_scrapers(self):
    scrapers = [
        CologneWatchScraper(),
        MySourceScraper(),  # Add here
    ]
    return scrapers
```

## Deployment (VPS)

### 1. Transfer to VPS

```bash
# On local machine
cd Watch_Service
rsync -avz --exclude 'venv' --exclude '*.log' backend/ root@72.62.148.205:~/Watch_Service/backend/
```

### 2. Setup on VPS

```bash
ssh root@72.62.148.205
cd ~/Watch_Service/backend
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # Add credentials
```

### 3. Test Manual Run

```bash
python3 watch_searcher.py
```

### 4. Setup Cronjob

```bash
crontab -e
```

Add:
```
# Watch Service - Hourly Search
0 * * * * cd ~/Watch_Service/backend && source venv/bin/activate && python3 watch_searcher.py >> watch_service.log 2>&1
```

## Development

### Testing a Single Scraper

```python
from scrapers.cologne_watch_scraper import CologneWatchScraper

scraper = CologneWatchScraper()
criteria = {
    'manufacturer': 'Rolex',
    'model': 'GMT-Master II'
}
listings = scraper.search(criteria)
print(f"Found {len(listings)} listings")
```

### Testing OpenAI Extraction

```python
from core.openai_extractor import OpenAIExtractor

extractor = OpenAIExtractor()
result = extractor.extract_watch_data(
    raw_text="<html>...</html>",
    source_name="Test Source",
    search_criteria={'manufacturer': 'Rolex', 'model': 'Submariner'}
)
print(result)
```

## Costs

- **OpenAI (GPT-4o-mini):** ~$0.002 per listing extraction
- **Expected:** ~€5-15/month depending on listing volume

## Next Steps

1. ✅ Core infrastructure (done)
2. ⏳ Add more scrapers (1-2 sources)
3. ⏳ Test with real searches
4. ⏳ Deploy to VPS
5. ⏳ Setup cronjobs
6. ⏳ Add all 15+ sources
