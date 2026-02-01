import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const source = searchParams.get('source')
    const availability = searchParams.get('availability')
    const limit = searchParams.get('limit')

    let query = 'SELECT * FROM watch_listings WHERE 1=1'
    const params: any[] = []
    let paramIndex = 1

    if (source) {
      query += ` AND source = $${paramIndex++}`
      params.push(source)
    }
    if (availability) {
      query += ` AND availability = $${paramIndex++}`
      params.push(availability)
    }

    query += ' ORDER BY date_found DESC'

    if (limit) {
      query += ` LIMIT $${paramIndex++}`
      params.push(parseInt(limit))
    }

    const { rows } = await sql.query(query, params)
    return NextResponse.json(rows)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
