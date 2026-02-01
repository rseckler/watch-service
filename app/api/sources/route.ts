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

export async function POST(request: Request) {
  try {
    const source = await request.json()

    const { rows } = await sql`
      INSERT INTO watch_sources (
        name, url, domain, type, scraper_type, active, requires_auth,
        rate_limit_seconds, search_url_template, listing_selector, title_selector,
        price_selector, link_selector, image_selector, auth_username_env,
        auth_password_env, notes
      ) VALUES (
        ${source.name}, ${source.url}, ${source.domain}, ${source.type},
        ${source.scraper_type}, ${source.active}, ${source.requires_auth},
        ${source.rate_limit_seconds}, ${source.search_url_template || null},
        ${source.listing_selector || null}, ${source.title_selector || null},
        ${source.price_selector || null}, ${source.link_selector || null},
        ${source.image_selector || null}, ${source.auth_username_env || null},
        ${source.auth_password_env || null}, ${source.notes || null}
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
      `UPDATE watch_sources SET ${setClause} WHERE id = $1 RETURNING *`,
      [id, ...values]
    )

    return NextResponse.json(rows[0])
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
