export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      watch_sources: {
        Row: {
          id: string
          name: string
          url: string
          domain: string
          type: 'Dealer' | 'Forum' | 'Marketplace'
          scraper_type: 'Static' | 'Dynamic'
          active: boolean
          requires_auth: boolean
          rate_limit_seconds: number
          search_url_template: string
          listing_selector: string | null
          title_selector: string | null
          price_selector: string | null
          link_selector: string | null
          image_selector: string | null
          custom_scraper: string | null
          auth_username_env: string | null
          auth_password_env: string | null
          last_successful_scrape: string | null
          error_count: number
          notes: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['watch_sources']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['watch_sources']['Insert']>
      }
      watch_search_criteria: {
        Row: {
          id: string
          name: string
          manufacturer: string
          model: string
          reference_number: string | null
          year: number | null
          allowed_countries: string[] | null
          active: boolean
          notes: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['watch_search_criteria']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['watch_search_criteria']['Insert']>
      }
      watch_listings: {
        Row: {
          id: string
          name: string
          date_found: string
          manufacturer: string | null
          model: string | null
          reference_number: string | null
          year: number | null
          condition: 'Neu' | 'Wie Neu' | 'Sehr Gut' | 'Gut' | 'Gebraucht' | 'Unbekannt' | null
          price: number | null
          currency: string
          location: string | null
          country: string | null
          link: string
          seller_name: string | null
          seller_url: string | null
          source: string
          source_type: 'Dealer' | 'Forum' | 'Marketplace' | null
          availability: 'Available' | 'Sold' | 'Unknown'
          sold_at: string | null
          last_checked: string
          url_hash: string
          search_criteria_id: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['watch_listings']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['watch_listings']['Insert']>
      }
      watch_sync_history: {
        Row: {
          id: string
          name: string
          date: string
          status: 'Success' | 'Partial' | 'Failed'
          sources_checked: number
          sources_failed: number
          listings_found: number
          listings_saved: number
          duplicates_skipped: number
          duration_seconds: number
          error_message: string | null
          created_at: string
        }
        Insert: Omit<Database['public']['Tables']['watch_sync_history']['Row'], 'id' | 'created_at'>
        Update: Partial<Database['public']['Tables']['watch_sync_history']['Insert']>
      }
    }
    Views: {}
    Functions: {}
    Enums: {}
  }
}
