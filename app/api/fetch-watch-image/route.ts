import { NextResponse } from 'next/server'
import { fetchWatchImage } from '@/lib/watch-image-fetcher'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { manufacturer, model, referenceNumber } = body

    if (!manufacturer || !model) {
      return NextResponse.json(
        { error: 'Manufacturer and model are required' },
        { status: 400 }
      )
    }

    const imageUrl = await fetchWatchImage({
      manufacturer,
      model,
      referenceNumber,
    })

    if (!imageUrl) {
      return NextResponse.json(
        { error: 'Could not find official image for this watch' },
        { status: 404 }
      )
    }

    return NextResponse.json({ imageUrl })
  } catch (error: any) {
    console.error('Error fetching watch image:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch watch image' },
      { status: 500 }
    )
  }
}
