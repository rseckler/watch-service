import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function POST() {
  try {
    // Add image_url columns
    await sql`ALTER TABLE watch_search_criteria ADD COLUMN IF NOT EXISTS image_url TEXT`
    await sql`ALTER TABLE watch_listings ADD COLUMN IF NOT EXISTS image_url TEXT`

    return NextResponse.json({
      success: true,
      message: 'Migration completed: Added image_url columns',
    })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
