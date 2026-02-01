# Deployment Checklist - Watch Service

Use this checklist to ensure proper deployment.

---

## Phase 1: Local Setup ✅

### Prerequisites
- [ ] Python 3.12+ installed
- [ ] Git installed
- [ ] Notion account created
- [ ] OpenAI account created
- [ ] Gmail account available

### Get API Keys (5 minutes)
- [ ] Notion API Key obtained from https://www.notion.so/my-integrations
  - Integration name: "Watch Service"
  - Capabilities: Read, Update, Insert content
  - Copy "Internal Integration Token"

- [ ] OpenAI API Key obtained from https://platform.openai.com/api-keys
  - Key name: "Watch Service"
  - Budget limit set: $50/month
  - Copy secret key

- [ ] Gmail App Password created
  - Google Account → Security → 2-Step Verification enabled
  - App Passwords → Generate for "Watch Service"
  - Copy 16-character password

### Project Setup (2 minutes)
- [ ] Navigate to project directory
  ```bash
  cd /Users/robin/Documents/4_AI/Watch_Service
  ```

- [ ] Create virtual environment
  ```bash
  python3 -m venv venv
  ```

- [ ] Activate virtual environment
  ```bash
  source venv/bin/activate
  ```

- [ ] Install dependencies
  ```bash
  pip3 install -r requirements.txt
  ```

- [ ] Verify installations
  ```bash
  pip3 list | grep -E "notion|openai|selenium|beautifulsoup4"
  ```

### Environment Configuration (1 minute)
- [ ] Create .env file
  ```bash
  cp .env.example .env
  ```

- [ ] Edit .env and add:
  - [ ] NOTION_API_KEY
  - [ ] OPENAI_API_KEY
  - [ ] SMTP_USER
  - [ ] SMTP_PASSWORD
  - [ ] RECIPIENT_EMAIL

- [ ] Verify .env file exists and is git-ignored
  ```bash
  cat .env | head -5  # Should show your keys
  git status          # Should NOT show .env
  ```

---

## Phase 2: Notion Setup ✅

### Create Parent Page (1 minute)
- [ ] Open Notion workspace
- [ ] Create new page titled "Watches"
- [ ] Copy page ID from URL
  - Format: `notion.so/workspace/PAGE_ID_HERE`
  - Save page ID for next step

### Run Setup Script (2 minutes)
- [ ] Execute setup script
  ```bash
  python3 setup_notion_databases.py
  ```

- [ ] When prompted, enter:
  - [ ] Notion API Key (from Phase 1)
  - [ ] Parent Page ID (from above)

- [ ] Verify output shows:
  - [ ] ✅ Sources DB created
  - [ ] ✅ Search Criteria DB created
  - [ ] ✅ Listings DB created
  - [ ] ✅ Sync History DB created
  - [ ] ✅ 17 sources populated
  - [ ] ✅ .env updated with database IDs

### Share Databases with Integration (CRITICAL!)
- [ ] In Notion, open **Sources** database
  - [ ] Click "..." (top right) → "Add connections"
  - [ ] Select "Watch Service" integration

- [ ] Repeat for **Watch_Search_Criteria** database
  - [ ] Click "..." → "Add connections" → "Watch Service"

- [ ] Repeat for **Watch_Listings** database
  - [ ] Click "..." → "Add connections" → "Watch Service"

- [ ] Repeat for **Sync_History** database
  - [ ] Click "..." → "Add connections" → "Watch Service"

### Add Search Criteria (2 minutes)
- [ ] Open **Watch_Search_Criteria** database in Notion

- [ ] Add first criterion:
  - [ ] Click "New"
  - [ ] Manufacturer: "Rolex"
  - [ ] Model: "Submariner"
  - [ ] Allowed_Countries: Select "Germany", "Austria", "Switzerland"
  - [ ] Active: ✓ (checked)

- [ ] Add more criteria (optional):
  - [ ] Omega Speedmaster
  - [ ] Patek Philippe Nautilus
  - [ ] Your desired watches

---

## Phase 3: Local Testing ✅

### Safe System Test (2 minutes)
- [ ] Run test script
  ```bash
  python3 test_complete_system.py
  ```

- [ ] Verify output shows:
  - [ ] ✅ Notion connection: PASS
  - [ ] ✅ Sources loaded: 17
  - [ ] ✅ Scraper test: PASS
  - [ ] ✅ OpenAI extraction: PASS
  - [ ] ✅ Duplicate detection: PASS
  - [ ] ✅ Email config: PASS

- [ ] Check logs
  ```bash
  cat test_system.log
  ```

### Manual Production Test (5 minutes)
- [ ] Run main search script
  ```bash
  python3 watch_searcher.py
  ```

- [ ] Watch console output for:
  - [ ] "🚀 Watch Service - Starting Search"
  - [ ] "📋 Loaded X sources and Y search criteria"
  - [ ] "🌐 Searching [source name]..."
  - [ ] "✅ Found X raw listings"
  - [ ] "💾 Saved Y new listings"
  - [ ] "📧 Sending email..."
  - [ ] "✅ Search completed successfully"

- [ ] Check Notion **Watch_Listings** database
  - [ ] New listings appear
  - [ ] All fields populated correctly
  - [ ] Links are clickable

- [ ] Check email inbox
  - [ ] Email received: "🎯 X neue Uhren gefunden!"
  - [ ] Email contains watch cards
  - [ ] Links in email work

- [ ] Check logs
  ```bash
  tail -50 watch_service.log
  ```

### Availability Checker Test (2 minutes)
- [ ] Run availability checker
  ```bash
  python3 availability_checker.py
  ```

- [ ] Verify output shows:
  - [ ] "🔍 Availability Checker - Starting"
  - [ ] "Checking X available listings"
  - [ ] "✅ Availability check completed"

- [ ] Check logs
  ```bash
  cat availability_check.log
  ```

---

## Phase 4: CSS Selector Validation ⚠️

### Important Note
The 17 pre-configured sources have **ESTIMATED** CSS selectors.
Before production, validate each source by inspecting actual HTML.

### Validation Process (per source)

#### Example: Cologne Watch
- [ ] Visit search URL in browser
  ```
  https://www.colognewatch.de/search?q=rolex+submariner
  ```

- [ ] Open DevTools (F12 or right-click → Inspect)

- [ ] Find repeating listing element
  - [ ] Look for container div/article
  - [ ] Right-click → Copy → Copy selector

- [ ] Find title element
  - [ ] Locate watch title/name
  - [ ] Right-click → Copy → Copy selector

- [ ] Find price element
  - [ ] Locate price text
  - [ ] Right-click → Copy → Copy selector

- [ ] Find link element
  - [ ] Locate link to watch details
  - [ ] Right-click → Copy → Copy selector

- [ ] Test selectors in DevTools console
  ```javascript
  document.querySelectorAll('.your-selector')
  // Should return array of matching elements
  ```

- [ ] Update Notion **Sources** database
  - [ ] Open source entry
  - [ ] Update Listing_Selector
  - [ ] Update Title_Selector
  - [ ] Update Price_Selector
  - [ ] Update Link_Selector
  - [ ] Save

#### Repeat for All Sources
- [ ] Cologne Watch (colognewatch.de)
- [ ] Watch Vice (watchvice.de)
- [ ] Watch.de
- [ ] Marks Uhren (marks-uhren.de)
- [ ] Rothfuss Watches (rothfuss-watches.de)
- [ ] Karmann Watches (karmannwatches.de)
- [ ] Eupen Feine Uhren (eupenfeineuhren.de)
- [ ] G-Abriel (g-abriel.de)
- [ ] Bachmann & Scher (bachmann-scher.de)
- [ ] Uhrforum.de (requires login)
- [ ] WatchLounge Forum (requires login)
- [ ] Uhr-Forum.org (requires login)
- [ ] eBay.de
- [ ] Kleinanzeigen.de
- [ ] Chrono24 (chrono24.de)
- [ ] Chronext (chronext.de)
- [ ] Uhrinstinkt (uhrinstinkt.de)

**Estimated time:** 10-15 minutes per source × 17 = 2-3 hours

**Note:** You can validate sources incrementally. Start with most important sources first.

---

## Phase 5: VPS Deployment ✅

### VPS Access
- [ ] SSH to Hostinger VPS
  ```bash
  ssh root@72.62.148.205
  ```

- [ ] Verify access and system info
  ```bash
  uname -a
  python3 --version
  ```

### Clone Repository
- [ ] Navigate to home directory
  ```bash
  cd ~
  ```

- [ ] Clone repository
  ```bash
  git clone <your-repo-url> Watch_Service
  # Or: git clone https://github.com/rseckler/Watch_Service.git
  ```

- [ ] Navigate to project
  ```bash
  cd Watch_Service
  ```

### Setup Environment
- [ ] Create virtual environment
  ```bash
  python3 -m venv venv
  ```

- [ ] Activate virtual environment
  ```bash
  source venv/bin/activate
  ```

- [ ] Install dependencies
  ```bash
  pip3 install -r requirements.txt
  ```

- [ ] Create .env file
  ```bash
  nano .env
  ```

- [ ] Copy all credentials from local .env
  - [ ] Paste into VPS .env
  - [ ] Save (Ctrl+X, Y, Enter)

- [ ] Verify .env
  ```bash
  cat .env | grep -E "NOTION|OPENAI|SMTP"
  ```

### Install Chrome/Chromium
- [ ] Update package lists
  ```bash
  apt-get update
  ```

- [ ] Install Chromium and ChromeDriver
  ```bash
  apt-get install -y chromium-browser chromium-chromedriver
  ```

- [ ] Verify installation
  ```bash
  chromium-browser --version
  chromedriver --version
  ```

### Test on VPS
- [ ] Run safe system test
  ```bash
  python3 test_complete_system.py
  ```

- [ ] Verify output shows all tests passing

- [ ] Run manual search
  ```bash
  python3 watch_searcher.py
  ```

- [ ] Monitor execution

- [ ] Check logs
  ```bash
  tail -f watch_service.log
  ```

- [ ] Verify listings saved to Notion

- [ ] Verify email received

### Setup Cronjobs
- [ ] Open crontab editor
  ```bash
  crontab -e
  ```

- [ ] Add hourly search job (runs at :00)
  ```bash
  0 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 watch_searcher.py >> watch_service.log 2>&1
  ```

- [ ] Add availability check job (runs at :30)
  ```bash
  30 * * * * cd ~/Watch_Service && source venv/bin/activate && python3 availability_checker.py >> availability_check.log 2>&1
  ```

- [ ] Save and exit (Ctrl+X, Y, Enter)

- [ ] Verify cronjobs installed
  ```bash
  crontab -l
  ```

- [ ] Check cron service is running
  ```bash
  systemctl status cron
  ```

### Monitor Initial Runs
- [ ] Wait for next hour

- [ ] Check logs after first run
  ```bash
  tail -f watch_service.log
  ```

- [ ] Verify listings in Notion

- [ ] Check email notifications

- [ ] Monitor for 72 hours

---

## Phase 6: Monitoring & Maintenance ✅

### Daily Checks (First Week)
- [ ] Check logs for errors
  ```bash
  ssh root@72.62.148.205
  cd ~/Watch_Service
  tail -100 watch_service.log | grep -E "ERROR|❌"
  ```

- [ ] Check Notion **Sync_History** database
  - [ ] Review Status (Success/Partial/Failed)
  - [ ] Check Sources_Failed count
  - [ ] Review Error_Message if any

- [ ] Check Notion **Sources** database
  - [ ] Review Error_Count per source
  - [ ] Identify failing sources
  - [ ] Update CSS selectors if needed

- [ ] Check email notifications
  - [ ] Confirm receiving alerts
  - [ ] Verify watch details correct

### Weekly Maintenance
- [ ] Review OpenAI usage
  - [ ] Visit https://platform.openai.com/usage
  - [ ] Verify within €20-30/month budget
  - [ ] Adjust if exceeding limit

- [ ] Review Notion **Watch_Listings**
  - [ ] Verify no duplicate listings
  - [ ] Check data quality
  - [ ] Review Availability status

- [ ] Update failing sources
  - [ ] Inspect HTML changes
  - [ ] Update CSS selectors in Notion
  - [ ] Re-enable if fixed

### Monthly Tasks
- [ ] Review all source configurations
  - [ ] Test each source manually
  - [ ] Update outdated selectors
  - [ ] Remove dead sources
  - [ ] Add new sources

- [ ] Optimize OpenAI costs
  - [ ] Review confidence threshold
  - [ ] Adjust HTML truncation length
  - [ ] Consider caching strategies

- [ ] Security audit
  - [ ] Rotate API keys if needed
  - [ ] Review .env on VPS
  - [ ] Check for exposed credentials

---

## Troubleshooting Checklist ✅

### "No active sources found"
- [ ] Verify setup_notion_databases.py ran successfully
- [ ] Check Notion **Sources** database exists
- [ ] Verify sources have Active checkbox checked
- [ ] Verify integration connected to database

### "Permission denied" error
- [ ] Verify databases shared with "Watch Service" integration
- [ ] Re-share all 4 databases
- [ ] Check Notion API key is correct

### "OpenAI API error"
- [ ] Verify OPENAI_API_KEY in .env
- [ ] Check OpenAI account has billing enabled
- [ ] Verify usage limit not exceeded
- [ ] Test API key manually

### "Email not sent"
- [ ] Verify SMTP credentials in .env
- [ ] Use Gmail App Password (not account password)
- [ ] Check 2-factor auth enabled
- [ ] Test SMTP connection manually

### Source always fails
- [ ] Inspect site HTML in browser
- [ ] Update CSS selectors in Notion
- [ ] Increase Rate_Limit_Seconds
- [ ] Check if site requires authentication
- [ ] Verify site is accessible from VPS

### "Selenium WebDriver failed"
- [ ] Verify Chrome/Chromium installed
  ```bash
  chromium-browser --version
  ```
- [ ] Check ChromeDriver version matches
- [ ] Test Selenium manually
  ```bash
  python3 -c "from selenium import webdriver; webdriver.Chrome()"
  ```
- [ ] Check headless mode setting

### Duplicate listings appearing
- [ ] Verify URL_Hash field populated
- [ ] Check get_existing_url_hashes() working
- [ ] Review duplicate detection logic
- [ ] Check if URL format changed

---

## Success Metrics ✅

### After 24 Hours
- [ ] At least 12/24 hourly runs completed
- [ ] At least 50% of sources successful
- [ ] Email notifications received for new listings
- [ ] No critical errors in logs
- [ ] Notion databases populated

### After 1 Week
- [ ] 168/168 hourly runs completed (100%)
- [ ] At least 80% of sources successful (14/17)
- [ ] 50+ listings found and saved
- [ ] Availability tracking working
- [ ] OpenAI costs within budget

### After 1 Month
- [ ] 720 hourly runs completed
- [ ] All validated sources working (100%)
- [ ] 200+ listings found
- [ ] Sold listings correctly marked
- [ ] Total cost €20-30/month
- [ ] No manual intervention needed

---

## Final Verification ✅

Before marking deployment complete:

- [ ] ✅ All 4 Notion databases created and shared
- [ ] ✅ 17 sources pre-configured in Notion
- [ ] ✅ At least 1 search criterion added
- [ ] ✅ Local tests passing
- [ ] ✅ Manual search finds listings
- [ ] ✅ Email notifications received
- [ ] ✅ VPS deployed and running
- [ ] ✅ Cronjobs executing hourly
- [ ] ✅ Logs being written correctly
- [ ] ✅ CSS selectors validated (or in progress)
- [ ] ✅ Monitoring in place
- [ ] ✅ Documentation reviewed

---

## Emergency Contacts ✅

- **OpenAI Issues:** https://help.openai.com
- **Notion Issues:** https://www.notion.so/help
- **VPS Issues:** Hostinger support
- **Project Issues:** rseckler@gmail.com

---

## Deployment Status

**Current Phase:** ________________
**Started:** ________________
**Completed:** ________________
**Status:** ________________

**Notes:**
```
[Add any deployment notes here]
```

---

**Last Updated:** 2026-02-01
**Version:** 1.0.0
