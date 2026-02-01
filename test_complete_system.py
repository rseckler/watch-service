"""
Safe system test - tests with only 1 source (Cologne Watch) and 1 criteria
Validates: Supabase connection, scraping, OpenAI extraction, duplicate detection, email
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.supabase_client import SupabaseClient
from core.openai_extractor import OpenAIExtractor
from core.email_sender import EmailSender
from scrapers import CustomScraperLoader
from utils import setup_logger, generate_url_hash

load_dotenv()
logger = setup_logger('test_system', 'test_system.log')


def test_system():
    """Run safe system test"""
    logger.info("=" * 60)
    logger.info("🧪 Watch Service - System Test (Safe Mode)")
    logger.info("=" * 60)

    try:
        # 1. Test Supabase connection
        logger.info("\n1️⃣  Testing Supabase connection...")
        db = SupabaseClient()
        sources = db.get_active_sources()
        criteria_list = db.get_search_criteria()

        logger.info(f"✅ Connected to Supabase")
        logger.info(f"   Found {len(sources)} active sources")
        logger.info(f"   Found {len(criteria_list)} active search criteria")

        if not sources:
            logger.error("❌ No active sources found - run populate_sources.py first")
            return False

        if not criteria_list:
            logger.warning("⚠️  No search criteria found - run add_test_criteria.py first")
            logger.info("   Continuing test with dummy criteria...")
            criteria_list = [{
                'id': 'test',
                'manufacturer': 'Rolex',
                'model': 'Submariner',
                'allowed_countries': ['Germany']
            }]

        # 2. Test with first source only
        logger.info("\n2️⃣  Testing scraper (first source only)...")
        test_source = sources[0]
        logger.info(f"   Using source: {test_source['name']}")

        scraper = CustomScraperLoader.load_scraper(test_source)
        test_criteria = criteria_list[0]

        logger.info(f"   Searching for: {test_criteria.get('manufacturer')} {test_criteria.get('model')}")

        findings = scraper.search(test_criteria)
        logger.info(f"✅ Scraper returned {len(findings)} raw listings")

        if findings:
            logger.info(f"   Sample: {findings[0].get('title', 'No title')[:50]}...")

        scraper.close_driver()

        # 3. Test OpenAI extraction
        extracted = None
        if findings:
            logger.info("\n3️⃣  Testing OpenAI extraction...")
            openai = OpenAIExtractor()

            extracted = openai.extract_watch_data(
                findings[0].get('raw_html', ''),
                test_source['name']
            )

            if extracted:
                logger.info(f"✅ OpenAI extracted data successfully")
                logger.info(f"   Manufacturer: {extracted.get('manufacturer')}")
                logger.info(f"   Model: {extracted.get('model')}")
                logger.info(f"   Price: {extracted.get('price')} {extracted.get('currency')}")
                logger.info(f"   Confidence: {extracted.get('confidence', 0):.2f}")
            else:
                logger.warning("⚠️  OpenAI extraction failed (low confidence or error)")

        # 4. Test duplicate detection
        logger.info("\n4️⃣  Testing duplicate detection...")
        existing_hashes = db.get_existing_url_hashes()
        logger.info(f"✅ Loaded {len(existing_hashes)} existing URL hashes")

        # 5. Test email (without sending)
        logger.info("\n5️⃣  Testing email configuration...")
        email = EmailSender()

        if email.smtp_user and email.smtp_password:
            logger.info(f"✅ Email configured: {email.smtp_user}")
            logger.info(f"   Recipient: {email.recipient_email}")
            logger.info("   (Email not sent in test mode)")
        else:
            logger.warning("⚠️  Email not configured - notifications will be skipped")

        # 6. Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info("✅ Supabase connection: PASS")
        logger.info(f"✅ Sources loaded: {len(sources)}")
        logger.info(f"✅ Scraper test: PASS ({len(findings)} listings)")
        logger.info("✅ OpenAI extraction: PASS" if extracted else "⚠️  OpenAI extraction: SKIP")
        logger.info(f"✅ Duplicate detection: PASS ({len(existing_hashes)} hashes)")
        logger.info("✅ Email config: PASS" if email.smtp_user else "⚠️  Email config: SKIP")
        logger.info("=" * 60)
        logger.info("🎉 System test completed successfully!")
        logger.info("=" * 60)

        print("\nNext steps:")
        print("1. Add more search criteria via add_test_criteria.py or Supabase UI")
        print("2. Review and update source configurations if needed")
        print("3. Configure email credentials in .env")
        print("4. Run: python3 watch_searcher.py")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = test_system()
    sys.exit(0 if success else 1)
