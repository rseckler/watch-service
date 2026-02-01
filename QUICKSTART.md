# Quick Start Guide - Watch Service

Get up and running in 15 minutes!

## Prerequisites

- Python 3.12+
- Notion account
- OpenAI API account
- Gmail account (for notifications)

## Step-by-Step Setup

### 1. Get API Keys (5 minutes)

#### Notion API Key
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name: "Watch Service"
4. Select workspace
5. Capabilities: ✓ Read, ✓ Update, ✓ Insert
6. Click "Submit"
7. Copy "Internal Integration Token" → Save for step 3

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name: "Watch Service"
4. Copy key → Save for step 3

#### Gmail App Password
1. Go to Google Account → Security
2. Enable 2-Step Verification (if not already)
3. Search "App passwords"
4. Select app: Mail, device: Other (Watch Service)
5. Click "Generate"
6. Copy 16-character password → Save for step 3

### 2. Setup Project (2 minutes)

```bash
# Clone/navigate to project
cd /Users/robin/Documents/4_AI/Watch_Service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

### 3. Configure Environment (1 minute)

```bash
# Create .env file
cp .env.example .env
nano .env
```

**Add your keys:**
```bash
# Paste your API keys from Step 1
NOTION_API_KEY=secret_xxx
OPENAI_API_KEY=sk-xxx
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=rseckler@gmail.com
```

Save and exit (Ctrl+X, Y, Enter).

### 4. Create Notion Databases (2 minutes)

```bash
python3 setup_notion_databases.py
```

**You'll be asked:**
1. **Notion API Key** - Paste the key from Step 1
2. **Parent Page ID** - Find it in Notion:
   - Create a new page called "Watches"
   - Copy the page ID from URL: `notion.so/workspace/<THIS-PART>`
   - Paste just the ID (without hyphens is fine)

**What happens:**
- ✅ Creates 4 databases (Sources, Criteria, Listings, History)
- ✅ Populates Sources with 17 pre-configured sources
- ✅ Updates .env with database IDs

### 5. Share Databases with Integration (IMPORTANT!)

In Notion:
1. Open each database (Sources, Watch_Search_Criteria, Watch_Listings, Sync_History)
2. Click "..." (top right) → "Add connections"
3. Select "Watch Service" integration
4. Repeat for all 4 databases

### 6. Add Search Criteria (1 minute)

In Notion, open **Watch_Search_Criteria** database:

1. Click "New"
2. Fill in:
   - **Name**: Rolex Submariner (auto-generated)
   - **Manufacturer**: Rolex
   - **Model**: Submariner
   - **Allowed_Countries**: Select Germany, Austria, Switzerland
   - **Active**: ✓ (check the box)
3. Click outside to save

**Add more watches:**
- Omega Speedmaster
- Patek Philippe Nautilus
- etc.

### 7. Test System (2 minutes)

```bash
python3 test_complete_system.py
```

**Expected output:**
```
🧪 Watch Service - System Test (Safe Mode)
==========================================

1️⃣  Testing Notion connection...
✅ Connected to Notion
   Found 17 active sources
   Found 1 active search criteria

2️⃣  Testing scraper (first source only)...
   Using source: Cologne Watch
✅ Scraper returned 5 raw listings

3️⃣  Testing OpenAI extraction...
✅ OpenAI extracted data successfully
   Manufacturer: Rolex
   Model: Submariner
   Price: 8999.0 EUR
   Confidence: 0.92

4️⃣  Testing duplicate detection...
✅ Loaded 0 existing URL hashes

5️⃣  Testing email configuration...
✅ Email configured: your-email@gmail.com

📊 TEST SUMMARY
==========================================
✅ All tests passed!
```

### 8. Run Manual Search (2 minutes)

```bash
python3 watch_searcher.py
```

**Watch the logs:**
- ✅ Searches ALL 17 sources
- ✅ Extracts data with OpenAI
- ✅ Saves to Notion
- ✅ Sends email notification

**Check Notion:**
- Open **Watch_Listings** database
- See new listings appear!
- Click links to view watches

**Check Email:**
- You should receive: "🎯 X neue Uhren gefunden!"

---

## You're Done! 🎉

The service is now ready. To run hourly automatically:

### Deploy to VPS (Optional)

```bash
# SSH to Hostinger VPS
ssh root@72.62.148.205

# Clone repository
cd ~
git clone <repo-url> Watch_Service
cd Watch_Service

# Setup (repeat steps 2-3 on VPS)
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
nano .env  # Add credentials

# Install Chrome for Selenium
apt-get update
apt-get install -y chromium-browser chromium-chromedriver

# Test
python3 watch_searcher.py

# Add cronjobs
crontab -e
```

**Add to crontab:**
```bash
# Hourly search
0 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 watch_searcher.py >> watch_service.log 2>&1

# Availability check (offset by 30 min)
30 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 availability_checker.py >> availability_check.log 2>&1
```

**Monitor:**
```bash
tail -f watch_service.log
```

---

## Next Steps

### Add More Sources

In Notion **Sources** database, click "New":

**Example: New dealer**
- Name: Example Watch Shop
- URL: https://example.com
- Domain: example.com
- Type: Dealer
- Scraper_Type: Static
- Active: ✓
- Rate_Limit_Seconds: 2
- Search_URL_Template: `https://example.com/search?q={manufacturer}+{model}`
- Listing_Selector: `.product` (inspect site HTML)
- Title_Selector: `.title`
- Price_Selector: `.price`
- Link_Selector: `a`

**Done!** Next hourly run will include this source.

### Update CSS Selectors

If a source stops working:
1. Open Notion **Sources** database
2. Find the source
3. Inspect website HTML in browser (F12)
4. Update selectors
5. Save

**No code deployment needed!**

### Customize Filters

Edit `core/openai_extractor.py`:
- Adjust confidence threshold
- Add price range filters
- Modify country matching logic

### Monitor Costs

- OpenAI dashboard: https://platform.openai.com/usage
- Expected: €20-30/month
- Set usage limit: $50/month

---

## Troubleshooting

### "No active sources found"
→ Run `python3 setup_notion_databases.py`

### "Permission denied" in Notion
→ Share databases with "Watch Service" integration

### "OpenAI API error"
→ Check API key, verify billing enabled

### "Email not sent"
→ Use Gmail App Password (not account password)

### Source always fails
→ Update CSS selectors in Notion Sources DB

---

**Need help?** Check README.md for detailed documentation.

**Questions?** Contact: rseckler@gmail.com
