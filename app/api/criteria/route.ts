import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const { rows } = await sql`SELECT * FROM watch_search_criteria ORDER BY created_at DESC`
    return NextResponse.json(rows)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const criteria = await request.json()

    const { rows } = await sql`
      INSERT INTO watch_search_criteria (
        name, manufacturer, model, reference_number, year, allowed_countries, active, notes
      ) VALUES (
        ${criteria.name}, ${criteria.manufacturer}, ${criteria.model},
        ${criteria.reference_number || null}, ${criteria.year || null},
        ${criteria.allowed_countries || []}, ${criteria.active !== false},
        ${criteria.notes || null}
      ) RETURNING *
    `

    return NextResponse.json(rows[0])
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
      `UPDATE watch_search_criteria SET ${setClause} WHERE id = $1 RETURNING *`,
      [id, ...values]
    )

    return NextResponse.json(rows[0])
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')

    if (!id) {
      return NextResponse.json({ error: 'ID required' }, { status: 400 })
    }

    await sql`DELETE FROM watch_search_criteria WHERE id = ${id}`
    return NextResponse.json({ success: true })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
