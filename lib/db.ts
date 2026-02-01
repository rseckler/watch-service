// Database client for Watch Service using API routes
// Client components call these functions which fetch from /api/* endpoints

export const db = {
  // Sources
  getSources: async () => {
    const res = await fetch('/api/sources')
    if (!res.ok) throw new Error('Failed to fetch sources')
    return res.json()
  },

  getActiveSources: async () => {
    const sources = await db.getSources()
    return sources.filter((s: any) => s.active)
  },

  updateSource: async (id: string, updates: any) => {
    const res = await fetch('/api/sources', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, updates }),
    })
    if (!res.ok) throw new Error('Failed to update source')
    return res.json()
  },

  // Search Criteria
  getCriteria: async () => {
    const res = await fetch('/api/criteria')
    if (!res.ok) throw new Error('Failed to fetch criteria')
    return res.json()
  },

  createCriteria: async (criteria: any) => {
    const res = await fetch('/api/criteria', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(criteria),
    })
    if (!res.ok) throw new Error('Failed to create criteria')
    return res.json()
  },

  updateCriteria: async (id: string, updates: any) => {
    const res = await fetch('/api/criteria', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, updates }),
    })
    if (!res.ok) throw new Error('Failed to update criteria')
    return res.json()
  },

  deleteCriteria: async (id: string) => {
    const res = await fetch(`/api/criteria?id=${id}`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('Failed to delete criteria')
    return res.json()
  },

  // Listings
  getListings: async (filters?: {
    source?: string
    availability?: string
    limit?: number
  }) => {
    const params = new URLSearchParams()
    if (filters?.source) params.append('source', filters.source)
    if (filters?.availability) params.append('availability', filters.availability)
    if (filters?.limit) params.append('limit', filters.limit.toString())

    const res = await fetch(`/api/listings?${params}`)
    if (!res.ok) throw new Error('Failed to fetch listings')
    return res.json()
  },

  // Sync History
  getSyncHistory: async (limit: number = 10) => {
    const res = await fetch(`/api/listings?limit=${limit}`)
    if (!res.ok) throw new Error('Failed to fetch sync history')
    return res.json()
  },

  // Statistics
  getStats: async () => {
    const res = await fetch('/api/stats')
    if (!res.ok) throw new Error('Failed to fetch stats')
    return res.json()
  },
}
