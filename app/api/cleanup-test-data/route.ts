import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

/**
 * DELETE endpoint to remove test listings
 * Deletes listings with url_hash starting with "test_hash_"
 */
export async function DELETE() {
  try {
    const { rowCount } = await sql`
      DELETE FROM watch_listings
      WHERE url_hash LIKE 'test_hash_%'
    `

    return NextResponse.json({
      success: true,
      message: `Deleted ${rowCount} test listings`,
      count: rowCount,
    })
  } catch (error: any) {
    console.error('Error deleting test data:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
