import { sql } from '@vercel/postgres'
import { NextResponse } from 'next/server'

// Status tracking for the current search
let currentSearchStatus = {
  isRunning: false,
  startedAt: null as Date | null,
  progress: {
    sourcesChecked: 0,
    totalSources: 0,
    listingsFound: 0,
    errors: [] as string[],
  },
}

export async function GET() {
  return NextResponse.json(currentSearchStatus)
}

export async function POST() {
  try {
    // Check if search is already running
    if (currentSearchStatus.isRunning) {
      return NextResponse.json(
        { error: 'Search is already running' },
        { status: 409 }
      )
    }

    // Start search
    currentSearchStatus = {
      isRunning: true,
      startedAt: new Date(),
      progress: {
        sourcesChecked: 0,
        totalSources: 0,
        listingsFound: 0,
        errors: [],
      },
    }

    // Run search asynchronously
    runSearch().catch((error) => {
      console.error('Search error:', error)
      currentSearchStatus.isRunning = false
      currentSearchStatus.progress.errors.push(error.message)
    })

    return NextResponse.json({
      success: true,
      message: 'Search started',
      status: currentSearchStatus,
    })
  } catch (error: any) {
    currentSearchStatus.isRunning = false
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

async function runSearch() {
  const startTime = Date.now()

  try {
    // 1. Get active sources
    const { rows: sources } = await sql\`
      SELECT * FROM watch_sources WHERE active = true ORDER BY name
    \`
    currentSearchStatus.progress.totalSources = sources.length

    // 2. Get active search criteria
    const { rows: criteria } = await sql\`
      SELECT * FROM watch_search_criteria WHERE active = true
    \`

    if (criteria.length === 0) {
      throw new Error('No active search criteria found')
    }

    let totalListingsFound = 0
    let totalSaved = 0
    let failedSources = 0

    // 3. For each source, simulate searching
    for (const source of sources) {
      try {
        currentSearchStatus.progress.sourcesChecked++

        // Simulate search delay
        await new Promise((resolve) => setTimeout(resolve, 1000))

        console.log(\`Searched \${source.name}\`)

        // Update last successful scrape
        await sql\`
          UPDATE watch_sources
          SET last_successful_scrape = NOW(), error_count = 0
          WHERE id = \${source.id}
        \`
      } catch (error: any) {
        failedSources++
        currentSearchStatus.progress.errors.push(
          \`\${source.name}: \${error.message}\`
        )

        // Update error count
        await sql\`
          UPDATE watch_sources
          SET error_count = error_count + 1
          WHERE id = \${source.id}
        \`
      }
    }

    // 4. Log to sync history
    const duration = Math.floor((Date.now() - startTime) / 1000)
    const status = failedSources === 0 ? 'Success' : failedSources < sources.length ? 'Partial' : 'Failed'

    await sql\`
      INSERT INTO watch_sync_history (
        name, date, status, sources_checked, sources_failed,
        listings_found, listings_saved, duplicates_skipped, duration_seconds
      ) VALUES (
        \${\`Manual Search \${new Date().toISOString()}\`},
        NOW(),
        \${status},
        \${currentSearchStatus.progress.sourcesChecked},
        \${failedSources},
        \${totalListingsFound},
        \${totalSaved},
        \${totalListingsFound - totalSaved},
        \${duration}
      )
    \`

    currentSearchStatus.progress.listingsFound = totalListingsFound

  } finally {
    currentSearchStatus.isRunning = false
  }
}
