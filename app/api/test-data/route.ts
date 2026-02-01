import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

export async function POST() {
  try {
    // Get the search criteria
    const { rows: criteria } = await sql`
      SELECT * FROM watch_search_criteria WHERE active = true LIMIT 1
    `

    if (criteria.length === 0) {
      return NextResponse.json({ error: 'No active search criteria found' }, { status: 400 })
    }

    const searchCriteria = criteria[0]

    // Create 3 realistic test listings
    const testListings = [
      {
        name: `${searchCriteria.manufacturer} ${searchCriteria.model} - Wie Neu`,
        manufacturer: searchCriteria.manufacturer,
        model: searchCriteria.model,
        reference_number: searchCriteria.reference_number,
        year: 2023,
        condition: 'Wie Neu',
        price: 15990,
        currency: 'EUR',
        location: 'München, Bayern',
        country: 'Germany',
        link: 'https://www.colognewatch.de/products/rolex-gmt-master-ii-126710blro',
        seller_name: 'Cologne Watch',
        seller_url: 'https://www.colognewatch.de',
        source: 'Cologne Watch',
        source_type: 'Dealer',
        availability: 'Available',
        url_hash: 'test_hash_001_' + Date.now(),
        image_url: searchCriteria.image_url || 'https://media.rolex.com/image/upload/q_auto:eco/f_auto/t_v7-majesty/c_limit,w_1200/v1/catalogue/2025/upright-c/m126710blro-0001',
      },
      {
        name: `${searchCriteria.manufacturer} ${searchCriteria.model} - Vollset`,
        manufacturer: searchCriteria.manufacturer,
        model: searchCriteria.model,
        reference_number: searchCriteria.reference_number,
        year: 2022,
        condition: 'Sehr Gut',
        price: 14500,
        currency: 'EUR',
        location: 'Berlin',
        country: 'Germany',
        link: 'https://www.watchvice.de/rolex-gmt-master-ii',
        seller_name: 'WatchVice',
        seller_url: 'https://www.watchvice.de',
        source: 'WatchVice',
        source_type: 'Dealer',
        availability: 'Available',
        url_hash: 'test_hash_002_' + Date.now(),
        image_url: searchCriteria.image_url || 'https://media.rolex.com/image/upload/q_auto:eco/f_auto/t_v7-majesty/c_limit,w_1200/v1/catalogue/2025/upright-c/m126710blro-0001',
      },
      {
        name: `${searchCriteria.manufacturer} ${searchCriteria.model} - Box & Papiere`,
        manufacturer: searchCriteria.manufacturer,
        model: searchCriteria.model,
        reference_number: searchCriteria.reference_number,
        year: 2024,
        condition: 'Neu',
        price: 16800,
        currency: 'EUR',
        location: 'Hamburg',
        country: 'Germany',
        link: 'https://www.chrono24.de/rolex/gmt-master-ii--id12345.htm',
        seller_name: 'Chrono24 Händler',
        seller_url: 'https://www.chrono24.de',
        source: 'Chrono24.de',
        source_type: 'Marketplace',
        availability: 'Available',
        url_hash: 'test_hash_003_' + Date.now(),
        image_url: searchCriteria.image_url || 'https://media.rolex.com/image/upload/q_auto:eco/f_auto/t_v7-majesty/c_limit,w_1200/v1/catalogue/2025/upright-c/m126710blro-0001',
      },
    ]

    const insertedListings = []

    for (const listing of testListings) {
      const { rows } = await sql`
        INSERT INTO watch_listings (
          name, manufacturer, model, reference_number, year, condition,
          price, currency, location, country, link, seller_name, seller_url,
          source, source_type, availability, url_hash, search_criteria_id,
          image_url, date_found, last_checked
        ) VALUES (
          ${listing.name}, ${listing.manufacturer}, ${listing.model},
          ${listing.reference_number}, ${listing.year}, ${listing.condition},
          ${listing.price}, ${listing.currency}, ${listing.location},
          ${listing.country}, ${listing.link}, ${listing.seller_name},
          ${listing.seller_url}, ${listing.source}, ${listing.source_type},
          ${listing.availability}, ${listing.url_hash}, ${searchCriteria.id},
          ${listing.image_url}, NOW(), NOW()
        ) RETURNING *
      `
      insertedListings.push(rows[0])
    }

    return NextResponse.json({
      success: true,
      message: `Created ${insertedListings.length} test listings`,
      listings: insertedListings,
    })
  } catch (error: any) {
    console.error('Error creating test data:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
