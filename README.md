# Watch Service Web App

Modern web application for managing luxury watch search criteria and viewing listings.

## Features

- 📋 **Dashboard** - Overview statistics and recent activity
- 🔍 **Search Criteria Management** - Add/edit/delete watches to search for
- 📦 **Listings View** - Browse all found watch listings with filters
- 🌐 **Sources Management** - Configure and monitor scraping sources
- ⚡ **Real-time Updates** - Automatically refreshes when new data is available

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Database:** Supabase (PostgreSQL)
- **State Management:** TanStack Query (React Query)
- **Deployment:** Vercel

## Setup

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your Supabase credentials:
```
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

3. Run development server:
```bash
npm run dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Manual

```bash
npm run build
npm run start
```

## Project Structure

```
web/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── criteria/          # Search Criteria management
│   ├── listings/          # Listings view
│   └── sources/           # Sources management
├── components/            # React components
│   ├── ui/               # UI primitives
│   └── ...               # Feature components
├── lib/                   # Utilities
│   ├── supabase.ts       # Supabase client
│   ├── types.ts          # TypeScript types
│   └── utils.ts          # Helper functions
└── public/               # Static assets
```

## Database Schema

The app connects to 4 Supabase tables:
- `watch_sources` - Scraping sources configuration
- `watch_search_criteria` - Watch models to search for
- `watch_listings` - Found watch listings
- `watch_sync_history` - Search run logs

## Development

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build
npm run build
```

## License

Private - Robin Seckler
