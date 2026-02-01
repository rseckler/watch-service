import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const [sources, criteria, listings, availableListings, syncHistory] = await Promise.all([
      sql`SELECT COUNT(*) as count FROM watch_sources`,
      sql`SELECT COUNT(*) as count FROM watch_search_criteria`,
      sql`SELECT COUNT(*) as count FROM watch_listings`,
      sql`SELECT COUNT(*) as count FROM watch_listings WHERE availability = 'Available'`,
      sql`SELECT * FROM watch_sync_history ORDER BY date DESC LIMIT 1`,
    ])

    return NextResponse.json({
      totalSources: parseInt(sources.rows[0].count),
      totalCriteria: parseInt(criteria.rows[0].count),
      totalListings: parseInt(listings.rows[0].count),
      availableListings: parseInt(availableListings.rows[0].count),
      lastSync: syncHistory.rows[0] || null,
    })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
