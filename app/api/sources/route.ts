import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const { rows } = await sql`SELECT * FROM watch_sources ORDER BY name`
    return NextResponse.json(rows)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function PATCH(request: Request) {
  try {
    const { id, updates } = await request.json()

    const fields = Object.keys(updates)
    const values = Object.values(updates)
    const setClause = fields.map((field, i) => `${field} = $${i + 2}`).join(', ')

    const { rows } = await sql.query(
      `UPDATE watch_sources SET ${setClause} WHERE id = $1 RETURNING *`,
      [id, ...values]
    )

    return NextResponse.json(rows[0])
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
