import { sql } from '@vercel/postgres'

// Helper functions for database queries using Neon PostgreSQL

export const db = {
  // Sources
  getSources: async () => {
    const { rows } = await sql`
      SELECT * FROM watch_sources ORDER BY name
    `
    return rows
  },

  getActiveSources: async () => {
    const { rows } = await sql`
      SELECT * FROM watch_sources WHERE active = true ORDER BY name
    `
    return rows
  },

  updateSource: async (id: string, updates: any) => {
    const fields = Object.keys(updates)
    const values = Object.values(updates)

    const setClause = fields.map((field, i) => `${field} = $${i + 2}`).join(', ')

    const { rows } = await sql.query(
      `UPDATE watch_sources SET ${setClause} WHERE id = $1 RETURNING *`,
      [id, ...values]
    )
    return rows[0]
  },

  // Search Criteria
  getCriteria: async () => {
    const { rows } = await sql`
      SELECT * FROM watch_search_criteria ORDER BY created_at DESC
    `
    return rows
  },

  createCriteria: async (criteria: any) => {
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
    return rows[0]
  },

  updateCriteria: async (id: string, updates: any) => {
    const fields = Object.keys(updates)
    const values = Object.values(updates)

    const setClause = fields.map((field, i) => `${field} = $${i + 2}`).join(', ')

    const { rows } = await sql.query(
      `UPDATE watch_search_criteria SET ${setClause} WHERE id = $1 RETURNING *`,
      [id, ...values]
    )
    return rows[0]
  },

  deleteCriteria: async (id: string) => {
    await sql`DELETE FROM watch_search_criteria WHERE id = ${id}`
  },

  // Listings
  getListings: async (filters?: {
    source?: string
    availability?: string
    limit?: number
  }) => {
    let query = 'SELECT * FROM watch_listings WHERE 1=1'
    const params: any[] = []
    let paramIndex = 1

    if (filters?.source) {
      query += ` AND source = $${paramIndex++}`
      params.push(filters.source)
    }
    if (filters?.availability) {
      query += ` AND availability = $${paramIndex++}`
      params.push(filters.availability)
    }

    query += ' ORDER BY date_found DESC'

    if (filters?.limit) {
      query += ` LIMIT $${paramIndex++}`
      params.push(filters.limit)
    }

    const { rows } = await sql.query(query, params)
    return rows
  },

  // Sync History
  getSyncHistory: async (limit: number = 10) => {
    const { rows } = await sql`
      SELECT * FROM watch_sync_history ORDER BY date DESC LIMIT ${limit}
    `
    return rows
  },

  // Statistics
  getStats: async () => {
    const [sources, criteria, listings, availableListings, syncHistory] = await Promise.all([
      sql`SELECT COUNT(*) as count FROM watch_sources`,
      sql`SELECT COUNT(*) as count FROM watch_search_criteria`,
      sql`SELECT COUNT(*) as count FROM watch_listings`,
      sql`SELECT COUNT(*) as count FROM watch_listings WHERE availability = 'Available'`,
      sql`SELECT * FROM watch_sync_history ORDER BY date DESC LIMIT 1`,
    ])

    return {
      totalSources: parseInt(sources.rows[0].count),
      totalCriteria: parseInt(criteria.rows[0].count),
      totalListings: parseInt(listings.rows[0].count),
      availableListings: parseInt(availableListings.rows[0].count),
      lastSync: syncHistory.rows[0] || null,
    }
  },
}
