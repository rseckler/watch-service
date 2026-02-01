import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

/**
 * POST endpoint to create test sync history logs
 * Creates 15 sample log entries for testing the archive view
 */
export async function POST() {
  try {
    const testLogs = []

    // Create 15 test log entries with varying data
    for (let i = 0; i < 15; i++) {
      const daysAgo = i
      const status = i % 3 === 0 ? 'Success' : i % 5 === 0 ? 'Partial' : 'Success'
      const date = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000)

      const { rows } = await sql`
        INSERT INTO watch_sync_history (
          name, date, status, sources_checked, sources_failed,
          listings_found, listings_saved, duplicates_skipped, duration_seconds
        ) VALUES (
          ${`Automatischer Suchlauf ${i + 1}`},
          ${date.toISOString()},
          ${status},
          ${15 + Math.floor(Math.random() * 3)},
          ${status === 'Partial' ? Math.floor(Math.random() * 3) : 0},
          ${Math.floor(Math.random() * 20)},
          ${Math.floor(Math.random() * 5)},
          ${Math.floor(Math.random() * 10)},
          ${45 + Math.floor(Math.random() * 60)}
        ) RETURNING id
      `

      testLogs.push(rows[0])
    }

    return NextResponse.json({
      success: true,
      message: `Created ${testLogs.length} test log entries`,
      count: testLogs.length,
    })
  } catch (error: any) {
    console.error('Error creating test logs:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

/**
 * DELETE endpoint to remove test logs
 */
export async function DELETE() {
  try {
    const { rowCount } = await sql`
      DELETE FROM watch_sync_history
      WHERE name LIKE 'Automatischer Suchlauf %'
    `

    return NextResponse.json({
      success: true,
      message: `Deleted ${rowCount} test log entries`,
      count: rowCount,
    })
  } catch (error: any) {
    console.error('Error deleting test logs:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
