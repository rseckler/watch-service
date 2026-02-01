#!/usr/bin/env node

/**
 * API-based database setup for Watch Service
 * Creates tables and populates sources using @vercel/postgres
 */

const { sql } = require('@vercel/postgres')

async function setupDatabase() {
  console.log('🚀 Starting database setup...\n')

  try {
    // ====================================================================
    // STEP 1: Create tables
    // ====================================================================

    console.log('📋 Creating tables...')

    // Table 1: watch_sources
    await sql`
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
      )
    `
    console.log('  ✅ watch_sources')

    // Table 2: watch_search_criteria
    await sql`
      CREATE TABLE IF NOT EXISTS watch_search_criteria (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        manufacturer VARCHAR(100) NOT NULL,
        model VARCHAR(100) NOT NULL,
        reference_number VARCHAR(50),
        year INTEGER,
        allowed_countries TEXT[],
        active BOOLEAN DEFAULT true,
        notes TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      )
    `
    console.log('  ✅ watch_search_criteria')

    // Table 3: watch_listings
    await sql`
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
      )
    `
    console.log('  ✅ watch_listings')

    // Table 4: watch_sync_history
    await sql`
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
      )
    `
    console.log('  ✅ watch_sync_history')

    // Create indexes
    console.log('\n📊 Creating indexes...')
    await sql`CREATE INDEX IF NOT EXISTS idx_sources_active ON watch_sources(active)`
    await sql`CREATE INDEX IF NOT EXISTS idx_sources_type ON watch_sources(type)`
    await sql`CREATE INDEX IF NOT EXISTS idx_criteria_active ON watch_search_criteria(active)`
    await sql`CREATE INDEX IF NOT EXISTS idx_criteria_manufacturer ON watch_search_criteria(manufacturer)`
    await sql`CREATE INDEX IF NOT EXISTS idx_listings_availability ON watch_listings(availability)`
    await sql`CREATE INDEX IF NOT EXISTS idx_listings_source ON watch_listings(source)`
    await sql`CREATE INDEX IF NOT EXISTS idx_listings_date_found ON watch_listings(date_found DESC)`
    await sql`CREATE INDEX IF NOT EXISTS idx_listings_url_hash ON watch_listings(url_hash)`
    await sql`CREATE INDEX IF NOT EXISTS idx_sync_history_date ON watch_sync_history(date DESC)`
    console.log('  ✅ All indexes created')

    // ====================================================================
    // STEP 2: Populate sources
    // ====================================================================

    console.log('\n🔧 Checking if sources already exist...')
    const { rows: existingSources } = await sql`SELECT COUNT(*) as count FROM watch_sources`

    if (parseInt(existingSources[0].count) > 0) {
      console.log(`  ⚠️  Found ${existingSources[0].count} existing sources. Skipping population.`)
    } else {
      console.log('  📝 Populating 17 sources...')

      // Dealers (9)
      const dealers = [
        ['Cologne Watch', 'https://www.colognewatch.de', 'colognewatch.de', 'https://www.colognewatch.de/search?q={manufacturer}+{model}', '.product-item', '.product-title', '.product-price', 'a.product-link', 'Premium dealer in Cologne'],
        ['WatchVice', 'https://www.watchvice.de', 'watchvice.de', 'https://www.watchvice.de/search?q={manufacturer}+{model}', '.product-card', 'h3.title', '.price', 'a.link', null],
        ['Watch.de', 'https://www.watch.de', 'watch.de', 'https://www.watch.de/suche?q={manufacturer}+{model}', '.watch-item', '.watch-name', '.watch-price', 'a', null],
        ['Marks Uhren', 'https://www.marks-uhren.de', 'marks-uhren.de', 'https://www.marks-uhren.de/search?q={manufacturer}+{model}', '.product', '.name', '.price-tag', 'a.product-link', null],
        ['Rothfuss Watches', 'https://www.rothfuss-watches.de', 'rothfuss-watches.de', 'https://www.rothfuss-watches.de/suche/{manufacturer}-{model}', '.item', '.title', '.preis', 'a', null],
        ['Karmann Watches', 'https://www.karmannwatches.de', 'karmannwatches.de', 'https://www.karmannwatches.de/search?q={manufacturer}+{model}', '.watch', 'h2', 'span.price', 'a.watch-link', null],
        ['Eupen Feine Uhren', 'https://www.eupenfeineuhren.de', 'eupenfeineuhren.de', 'https://www.eupenfeineuhren.de/suche?q={manufacturer}+{model}', '.product-box', '.product-title', '.price', 'a', null],
        ['G-Abriel', 'https://www.g-abriel.de', 'g-abriel.de', 'https://www.g-abriel.de/search/{manufacturer}+{model}', '.article', 'h3.name', '.price-value', 'a', null],
        ['Bachmann & Scher', 'https://www.bachmann-scher.de', 'bachmann-scher.de', 'https://www.bachmann-scher.de/suche?q={manufacturer}+{model}', '.product', '.title', '.price-tag', 'a.link', null],
      ]

      for (const [name, url, domain, search_url, list_sel, title_sel, price_sel, link_sel, notes] of dealers) {
        await sql`
          INSERT INTO watch_sources (
            name, url, domain, type, scraper_type, active,
            search_url_template, listing_selector, title_selector, price_selector, link_selector,
            rate_limit_seconds, notes
          ) VALUES (
            ${name}, ${url}, ${domain}, 'Dealer', 'Static', true,
            ${search_url}, ${list_sel}, ${title_sel}, ${price_sel}, ${link_sel},
            2, ${notes}
          )
        `
      }
      console.log('    ✅ 9 Dealers')

      // Forums (3)
      const forums = [
        ['Uhrforum.de', 'https://www.uhrforum.de', 'uhrforum.de', 'UHRFORUM_USERNAME', 'UHRFORUM_PASSWORD', 'https://www.uhrforum.de/search?q={manufacturer}+{model}', '.thread', '.thread-title', 'a.thread-link', 'Requires login: robin@seckler.de'],
        ['Watch Lounge Forum', 'https://forum.watchlounge.com', 'forum.watchlounge.com', 'WATCHLOUNGE_USERNAME', 'WATCHLOUNGE_PASSWORD', 'https://forum.watchlounge.com/search?q={manufacturer}+{model}', 'article.post', 'h3.title', 'a.permalink', null],
        ['Uhr-Forum.org', 'https://www.uhr-forum.org', 'uhr-forum.org', 'UHR_FORUM_ORG_USERNAME', 'UHR_FORUM_ORG_PASSWORD', 'https://www.uhr-forum.org/search?q={manufacturer}+{model}', '.post', '.post-title', 'a.link', null],
      ]

      for (const [name, url, domain, user_env, pass_env, search_url, list_sel, title_sel, link_sel, notes] of forums) {
        await sql`
          INSERT INTO watch_sources (
            name, url, domain, type, scraper_type, active, requires_auth,
            auth_username_env, auth_password_env,
            search_url_template, listing_selector, title_selector, link_selector,
            rate_limit_seconds, notes
          ) VALUES (
            ${name}, ${url}, ${domain}, 'Forum', 'Forum', true, true,
            ${user_env}, ${pass_env},
            ${search_url}, ${list_sel}, ${title_sel}, ${link_sel},
            3, ${notes}
          )
        `
      }
      console.log('    ✅ 3 Forums')

      // Marketplaces (5)
      const marketplaces = [
        ['eBay.de', 'https://www.ebay.de', 'ebay.de', false, null, null, 'https://www.ebay.de/sch/i.html?_nkw={manufacturer}+{model}', '.s-item', '.s-item__title', '.s-item__price', 'a.s-item__link', 'Use eBay API if possible'],
        ['Kleinanzeigen.de', 'https://www.kleinanzeigen.de', 'kleinanzeigen.de', true, 'KLEINANZEIGEN_USERNAME', 'KLEINANZEIGEN_PASSWORD', 'https://www.kleinanzeigen.de/s-{manufacturer}-{model}/k0', '.ad-listitem', '.text-module-begin', '.aditem-main--middle--price', 'a.ellipsis', 'Login: seckler@seckler.de'],
        ['Chrono24.de', 'https://www.chrono24.de', 'chrono24.de', false, null, null, 'https://www.chrono24.de/search/index.htm?query={manufacturer}+{model}', '.article-item', '.article-title', '.article-price', 'a.article-link', 'Premium marketplace'],
        ['Chronext.de', 'https://www.chronext.de', 'chronext.de', false, null, null, 'https://www.chronext.de/search?query={manufacturer}+{model}', '.watch-card', '.watch-name', '.watch-price', 'a', null],
        ['Uhrinstinkt.de', 'https://www.uhrinstinkt.de', 'uhrinstinkt.de', false, null, null, 'https://www.uhrinstinkt.de/search?q={manufacturer}+{model}', '.listing', '.listing-title', '.listing-price', 'a.listing-link', null],
      ]

      for (const [name, url, domain, requires_auth, user_env, pass_env, search_url, list_sel, title_sel, price_sel, link_sel, notes] of marketplaces) {
        await sql`
          INSERT INTO watch_sources (
            name, url, domain, type, scraper_type, active, requires_auth,
            auth_username_env, auth_password_env,
            search_url_template, listing_selector, title_selector, price_selector, link_selector,
            rate_limit_seconds, notes
          ) VALUES (
            ${name}, ${url}, ${domain}, 'Marketplace', 'Marketplace', true, ${requires_auth},
            ${user_env}, ${pass_env},
            ${search_url}, ${list_sel}, ${title_sel}, ${price_sel}, ${link_sel},
            ${name === 'eBay.de' || name === 'Kleinanzeigen.de' ? 5 : 3}, ${notes}
          )
        `
      }
      console.log('    ✅ 5 Marketplaces')
    }

    // ====================================================================
    // STEP 3: Verify
    // ====================================================================

    console.log('\n✅ Verifying setup...')

    const { rows: stats } = await sql`
      SELECT
        type,
        COUNT(*) as count,
        COUNT(CASE WHEN active THEN 1 END) as active_count
      FROM watch_sources
      GROUP BY type
      ORDER BY type
    `

    console.log('\n📊 Sources Summary:')
    stats.forEach(row => {
      console.log(`   ${row.type}: ${row.count} total, ${row.active_count} active`)
    })

    const totalSources = stats.reduce((sum, row) => sum + parseInt(row.count), 0)
    console.log(`   TOTAL: ${totalSources} sources`)

    console.log('\n🎉 Database setup complete!')
    console.log('\n🌐 Test your app: https://watch-service.vercel.app/sources')

  } catch (error) {
    console.error('\n❌ Error during setup:', error.message)
    console.error(error)
    process.exit(1)
  }
}

// Run setup
setupDatabase()
