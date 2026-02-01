import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check connection
    const { rows: test } = await sql`SELECT NOW() as current_time`

    // Check tables
    const { rows: tables } = await sql`
      SELECT tablename FROM pg_tables
      WHERE schemaname = 'public'
      AND tablename LIKE 'watch_%'
    `

    // Count sources
    const { rows: sourceCount } = await sql`SELECT COUNT(*) as count FROM watch_sources`

    // Get all sources
    const { rows: sources } = await sql`SELECT * FROM watch_sources ORDER BY name`

    // Check environment
    const env = {
      POSTGRES_URL: process.env.POSTGRES_URL ? 'Set (hidden)' : 'NOT SET',
      POSTGRES_PRISMA_URL: process.env.POSTGRES_PRISMA_URL ? 'Set (hidden)' : 'NOT SET',
    }

    return NextResponse.json({
      connection: 'OK',
      currentTime: test[0].current_time,
      tables: tables,
      sourceCount: sourceCount[0].count,
      sources: sources,
      environment: env,
    })
  } catch (error: any) {
    return NextResponse.json({
      error: error.message,
      stack: error.stack,
    }, { status: 500 })
  }
}
