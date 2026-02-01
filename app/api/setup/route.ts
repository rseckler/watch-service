import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    console.log('🚀 Starting database setup...')

    // Create tables
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

    // Create indexes
    await sql`CREATE INDEX IF NOT EXISTS idx_sources_active ON watch_sources(active)`
    await sql`CREATE INDEX IF NOT EXISTS idx_sources_type ON watch_sources(type)`
    await sql`CREATE INDEX IF NOT EXISTS idx_criteria_active ON watch_search_criteria(active)`
    await sql`CREATE INDEX IF NOT EXISTS idx_listings_availability ON watch_listings(availability)`
    await sql`CREATE INDEX IF NOT EXISTS idx_listings_date_found ON watch_listings(date_found DESC)`

    // Check if sources exist
    const { rows: existingSources } = await sql`SELECT COUNT(*) as count FROM watch_sources`

    if (parseInt(existingSources[0].count) === 0) {
      // Insert dealers
      const dealers = [
        ['Cologne Watch', 'https://www.colognewatch.de', 'colognewatch.de', 'https://www.colognewatch.de/search?q={manufacturer}+{model}', 'Premium dealer'],
        ['WatchVice', 'https://www.watchvice.de', 'watchvice.de', 'https://www.watchvice.de/search?q={manufacturer}+{model}', null],
        ['Watch.de', 'https://www.watch.de', 'watch.de', 'https://www.watch.de/suche?q={manufacturer}+{model}', null],
        ['Marks Uhren', 'https://www.marks-uhren.de', 'marks-uhren.de', 'https://www.marks-uhren.de/search?q={manufacturer}+{model}', null],
        ['Rothfuss Watches', 'https://www.rothfuss-watches.de', 'rothfuss-watches.de', 'https://www.rothfuss-watches.de/suche/{manufacturer}-{model}', null],
        ['Karmann Watches', 'https://www.karmannwatches.de', 'karmannwatches.de', 'https://www.karmannwatches.de/search?q={manufacturer}+{model}', null],
        ['Eupen Feine Uhren', 'https://www.eupenfeineuhren.de', 'eupenfeineuhren.de', 'https://www.eupenfeineuhren.de/suche?q={manufacturer}+{model}', null],
        ['G-Abriel', 'https://www.g-abriel.de', 'g-abriel.de', 'https://www.g-abriel.de/search/{manufacturer}+{model}', null],
        ['Bachmann & Scher', 'https://www.bachmann-scher.de', 'bachmann-scher.de', 'https://www.bachmann-scher.de/suche?q={manufacturer}+{model}', null],
      ]

      for (const [name, url, domain, search_url, notes] of dealers) {
        await sql`
          INSERT INTO watch_sources (name, url, domain, type, scraper_type, active, search_url_template, rate_limit_seconds, notes)
          VALUES (${name}, ${url}, ${domain}, 'Dealer', 'Static', true, ${search_url}, 2, ${notes})
        `
      }

      // Insert forums
      const forums = [
        ['Uhrforum.de', 'https://www.uhrforum.de', 'uhrforum.de', 'https://www.uhrforum.de/search?q={manufacturer}+{model}', 'UHRFORUM_USERNAME', 'UHRFORUM_PASSWORD'],
        ['Watch Lounge', 'https://forum.watchlounge.com', 'forum.watchlounge.com', 'https://forum.watchlounge.com/search?q={manufacturer}+{model}', 'WATCHLOUNGE_USERNAME', 'WATCHLOUNGE_PASSWORD'],
        ['Uhr-Forum.org', 'https://www.uhr-forum.org', 'uhr-forum.org', 'https://www.uhr-forum.org/search?q={manufacturer}+{model}', 'UHR_FORUM_ORG_USERNAME', 'UHR_FORUM_ORG_PASSWORD'],
      ]

      for (const [name, url, domain, search_url, user_env, pass_env] of forums) {
        await sql`
          INSERT INTO watch_sources (name, url, domain, type, scraper_type, active, requires_auth, auth_username_env, auth_password_env, search_url_template, rate_limit_seconds)
          VALUES (${name}, ${url}, ${domain}, 'Forum', 'Forum', true, true, ${user_env}, ${pass_env}, ${search_url}, 3)
        `
      }

      // Insert marketplaces
      const marketplaces = [
        ['eBay.de', 'https://www.ebay.de', 'ebay.de', false, null, null, 'https://www.ebay.de/sch/i.html?_nkw={manufacturer}+{model}', 5],
        ['Kleinanzeigen.de', 'https://www.kleinanzeigen.de', 'kleinanzeigen.de', true, 'KLEINANZEIGEN_USERNAME', 'KLEINANZEIGEN_PASSWORD', 'https://www.kleinanzeigen.de/s-{manufacturer}-{model}/k0', 5],
        ['Chrono24.de', 'https://www.chrono24.de', 'chrono24.de', false, null, null, 'https://www.chrono24.de/search/index.htm?query={manufacturer}+{model}', 3],
        ['Chronext.de', 'https://www.chronext.de', 'chronext.de', false, null, null, 'https://www.chronext.de/search?query={manufacturer}+{model}', 3],
        ['Uhrinstinkt.de', 'https://www.uhrinstinkt.de', 'uhrinstinkt.de', false, null, null, 'https://www.uhrinstinkt.de/search?q={manufacturer}+{model}', 2],
      ]

      for (const [name, url, domain, requires_auth, user_env, pass_env, search_url, rate_limit] of marketplaces) {
        await sql`
          INSERT INTO watch_sources (name, url, domain, type, scraper_type, active, requires_auth, auth_username_env, auth_password_env, search_url_template, rate_limit_seconds)
          VALUES (${name}, ${url}, ${domain}, 'Marketplace', 'Marketplace', true, ${requires_auth}, ${user_env}, ${pass_env}, ${search_url}, ${rate_limit})
        `
      }
    }

    // Get stats
    const { rows: stats } = await sql`
      SELECT type, COUNT(*) as count, COUNT(CASE WHEN active THEN 1 END) as active_count
      FROM watch_sources
      GROUP BY type
      ORDER BY type
    `

    return NextResponse.json({
      success: true,
      message: 'Database setup complete!',
      stats: stats,
    })
  } catch (error: any) {
    console.error('Setup error:', error)
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    )
  }
}
