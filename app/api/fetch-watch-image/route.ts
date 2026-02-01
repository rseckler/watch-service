import { NextResponse } from 'next/server'
import { fetchWatchImage } from '@/lib/watch-image-fetcher'

export async function POST(request: Request) {
  try {
    console.log('📸 Image fetch API called')

    const body = await request.json()
    const { manufacturer, model, referenceNumber } = body

    console.log('Watch details:', { manufacturer, model, referenceNumber })

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

    console.log('Image URL result:', imageUrl)

    if (!imageUrl) {
      return NextResponse.json(
        {
          error: 'Could not find official image for this watch',
          details: 'Tried pattern matching and OpenAI fallback'
        },
        { status: 404 }
      )
    }

    return NextResponse.json({ imageUrl })
  } catch (error: any) {
    console.error('❌ Error fetching watch image:', error)
    console.error('Error stack:', error.stack)
    return NextResponse.json(
      {
        error: error.message || 'Failed to fetch watch image',
        details: error.stack
      },
      { status: 500 }
    )
  }
}
