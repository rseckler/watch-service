import { createClient } from '@supabase/supabase-js'
import { Database } from './types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey)

// Helper functions for common queries
export const db = {
  // Sources
  getSources: async () => {
    const { data, error } = await supabase
      .from('watch_sources')
      .select('*')
      .order('name')
    if (error) throw error
    return data
  },

  getActiveSources: async () => {
    const { data, error } = await supabase
      .from('watch_sources')
      .select('*')
      .eq('active', true)
      .order('name')
    if (error) throw error
    return data
  },

  updateSource: async (id: string, updates: any) => {
    const { data, error } = await supabase
      .from('watch_sources')
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    if (error) throw error
    return data
  },

  // Search Criteria
  getCriteria: async () => {
    const { data, error } = await supabase
      .from('watch_search_criteria')
      .select('*')
      .order('created_at', { ascending: false })
    if (error) throw error
    return data
  },

  createCriteria: async (criteria: Database['public']['Tables']['watch_search_criteria']['Insert']) => {
    const { data, error } = await supabase
      .from('watch_search_criteria')
      .insert(criteria)
      .select()
      .single()
    if (error) throw error
    return data
  },

  updateCriteria: async (id: string, updates: any) => {
    const { data, error } = await supabase
      .from('watch_search_criteria')
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    if (error) throw error
    return data
  },

  deleteCriteria: async (id: string) => {
    const { error } = await supabase
      .from('watch_search_criteria')
      .delete()
      .eq('id', id)
    if (error) throw error
  },

  // Listings
  getListings: async (filters?: {
    source?: string
    availability?: string
    limit?: number
  }) => {
    let query = supabase
      .from('watch_listings')
      .select('*')
      .order('date_found', { ascending: false })

    if (filters?.source) {
      query = query.eq('source', filters.source)
    }
    if (filters?.availability) {
      query = query.eq('availability', filters.availability)
    }
    if (filters?.limit) {
      query = query.limit(filters.limit)
    }

    const { data, error } = await query
    if (error) throw error
    return data
  },

  // Sync History
  getSyncHistory: async (limit: number = 10) => {
    const { data, error } = await supabase
      .from('watch_sync_history')
      .select('*')
      .order('date', { ascending: false })
      .limit(limit)
    if (error) throw error
    return data
  },

  // Statistics
  getStats: async () => {
    const [sources, criteria, listings, availableListings, syncHistory] = await Promise.all([
      supabase.from('watch_sources').select('id', { count: 'exact', head: true }),
      supabase.from('watch_search_criteria').select('id', { count: 'exact', head: true }),
      supabase.from('watch_listings').select('id', { count: 'exact', head: true }),
      supabase.from('watch_listings').select('id', { count: 'exact', head: true }).eq('availability', 'Available'),
      supabase.from('watch_sync_history').select('*').order('date', { ascending: false }).limit(1),
    ])

    return {
      totalSources: sources.count || 0,
      totalCriteria: criteria.count || 0,
      totalListings: listings.count || 0,
      availableListings: availableListings.count || 0,
      lastSync: syncHistory.data?.[0] || null,
    }
  },
}
