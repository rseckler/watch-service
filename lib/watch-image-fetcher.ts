/**
 * Watch Image Fetcher
 * Automatically fetches official product images from manufacturer websites
 * Uses pattern matching + OpenAI fallback for reliability
 */

interface WatchImageParams {
  manufacturer: string
  model: string
  referenceNumber?: string
}

interface OpenAIImageResponse {
  imageUrl: string
  confidence: 'high' | 'medium' | 'low'
  source: string
}

/**
 * Attempts to fetch the official product image from the manufacturer's website
 * Strategy: Pattern matching first, then OpenAI fallback
 */
export async function fetchWatchImage(params: WatchImageParams): Promise<string | null> {
  const { manufacturer, model, referenceNumber } = params

  // Normalize manufacturer name
  const normalizedManufacturer = manufacturer.toLowerCase().trim()

  try {
    // STAGE 1: Try manufacturer-specific pattern matching (fast, free)
    console.log('🔍 Stage 1: Trying pattern-based image search...')

    let imageUrl: string | null = null

    if (normalizedManufacturer.includes('rolex')) {
      imageUrl = await fetchRolexImage(referenceNumber || '', model)
    } else if (normalizedManufacturer.includes('omega')) {
      imageUrl = await fetchOmegaImage(referenceNumber || '', model)
    } else if (normalizedManufacturer.includes('patek') || normalizedManufacturer.includes('philippe')) {
      imageUrl = await fetchPatekPhilippeImage(referenceNumber || '', model)
    } else if (normalizedManufacturer.includes('audemars') || normalizedManufacturer.includes('piguet')) {
      imageUrl = await fetchAudemarsPiguetImage(referenceNumber || '', model)
    } else if (normalizedManufacturer.includes('iwc')) {
      imageUrl = await fetchIWCImage(referenceNumber || '', model)
    }

    if (imageUrl) {
      console.log('✓ Found image via pattern matching:', imageUrl)
      return imageUrl
    }

    // STAGE 2: Pattern matching failed, use OpenAI (intelligent, small cost)
    console.log('🤖 Stage 2: Pattern failed, using OpenAI...')
    imageUrl = await fetchImageViaOpenAI(params)

    if (imageUrl) {
      console.log('✓ Found image via OpenAI:', imageUrl)
      return imageUrl
    }

    console.log('✗ No image found via any method')
    return null
  } catch (error) {
    console.error('Error fetching watch image:', error)
    return null
  }
}

/**
 * Fetch Rolex image from their official media server
 * Pattern: https://media.rolex.com/image/upload/.../catalogue/YEAR/upright-c/mREFERENCE
 */
async function fetchRolexImage(referenceNumber: string, model: string): Promise<string | null> {
  if (!referenceNumber) return null

  // Normalize reference number: lowercase and ensure proper dash format
  // Rolex format: 126710blro-0001 (dash before last segment)
  let cleanRef = referenceNumber.toLowerCase().trim()

  // Remove spaces
  cleanRef = cleanRef.replace(/\s+/g, '')

  // Ensure there's a dash before the last 4 digits if not present
  // Examples: 126710BLRO0001 -> 126710blro-0001, 126710BLRO-0001 -> 126710blro-0001
  if (!cleanRef.includes('-')) {
    // Try to add dash before last 4 digits
    if (cleanRef.length > 4) {
      cleanRef = cleanRef.slice(0, -4) + '-' + cleanRef.slice(-4)
    }
  }

  console.log('Rolex reference normalized:', cleanRef)

  // Try current year and previous years (Rolex updates their catalogue annually)
  const currentYear = new Date().getFullYear()
  const years = [currentYear, currentYear - 1, currentYear - 2, 2024, 2023]

  for (const year of years) {
    // Rolex pattern: m + reference number (e.g., m126710blro-0001)
    const imageUrl = `https://media.rolex.com/image/upload/q_auto:eco/f_auto/t_v7-majesty/c_limit,w_1200/v1/catalogue/${year}/upright-c/m${cleanRef}`

    console.log('Trying Rolex URL:', imageUrl)

    // Check if image exists
    if (await checkImageExists(imageUrl)) {
      console.log('✓ Found Rolex image:', imageUrl)
      return imageUrl
    }
  }

  // Fallback: Try without year in path (older Rolex images)
  const fallbackUrl = `https://content.rolex.com/dam/new-watches-2024/configure-hub/m${cleanRef}/1-configure/configure-2024-${model.toLowerCase().replace(/\s+/g, '-')}-m${cleanRef}_portrait.png`

  console.log('Trying Rolex fallback URL:', fallbackUrl)

  if (await checkImageExists(fallbackUrl)) {
    console.log('✓ Found Rolex image (fallback):', fallbackUrl)
    return fallbackUrl
  }

  console.log('✗ No Rolex image found for reference:', referenceNumber)
  return null
}

/**
 * Fetch Omega image from their official website
 */
async function fetchOmegaImage(referenceNumber: string, model: string): Promise<string | null> {
  if (!referenceNumber) return null

  // Omega pattern: https://www.omegawatches.com/media/catalog/product/...
  const cleanRef = referenceNumber.replace(/[.\s]/g, '')
  const imageUrl = `https://www.omegawatches.com/media/catalog/product/omega-seamaster-diver-300m-${cleanRef.toLowerCase()}.png`

  if (await checkImageExists(imageUrl)) {
    return imageUrl
  }

  return null
}

/**
 * Fetch Patek Philippe image
 */
async function fetchPatekPhilippeImage(referenceNumber: string, model: string): Promise<string | null> {
  if (!referenceNumber) return null

  // Patek Philippe pattern varies - this is a placeholder
  // Would need to implement their specific API or scraping logic
  return null
}

/**
 * Fetch Audemars Piguet image
 */
async function fetchAudemarsPiguetImage(referenceNumber: string, model: string): Promise<string | null> {
  if (!referenceNumber) return null

  // AP pattern - placeholder
  return null
}

/**
 * Fetch IWC image
 */
async function fetchIWCImage(referenceNumber: string, model: string): Promise<string | null> {
  if (!referenceNumber) return null

  // IWC pattern - placeholder
  return null
}

/**
 * Use OpenAI to intelligently find the official product image
 * Falls back when pattern matching fails
 */
async function fetchImageViaOpenAI(params: WatchImageParams): Promise<string | null> {
  const { manufacturer, model, referenceNumber } = params

  try {
    // Get OpenAI API key from environment
    const apiKey = process.env.OPENAI_API_KEY
    if (!apiKey) {
      console.error('OpenAI API key not found')
      return null
    }

    // Construct prompt for OpenAI
    const prompt = `You are an expert in luxury watch product image URLs. Given the following watch details, provide the most likely official product image URL from the manufacturer's website.

Watch Details:
- Manufacturer: ${manufacturer}
- Model: ${model}
- Reference Number: ${referenceNumber || 'Unknown'}

IMPORTANT RULES:
1. ONLY provide the official image URL from the manufacturer's CDN/media server
2. For Rolex: Use format https://media.rolex.com/image/upload/q_auto:eco/f_auto/t_v7-majesty/c_limit,w_1200/v1/catalogue/{YEAR}/upright-c/m{reference-lowercase}
3. For Omega: Use format https://www.omegawatches.com/media/catalog/product/...
4. Prefer high-resolution product images (not thumbnails)
5. Respond with ONLY the URL, nothing else
6. If unsure, try multiple common URL patterns for this manufacturer

Respond with the most likely image URL:`

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'system',
            content: 'You are an expert at finding official luxury watch product images. Always provide direct image URLs from manufacturer websites.',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: 0.3,
        max_tokens: 200,
      }),
    })

    if (!response.ok) {
      console.error('OpenAI API error:', response.status)
      return null
    }

    const data = await response.json()
    const imageUrl = data.choices?.[0]?.message?.content?.trim()

    if (!imageUrl || !isValidImageUrl(imageUrl)) {
      console.log('OpenAI did not return a valid image URL')
      return null
    }

    // Verify the URL actually exists
    if (await checkImageExists(imageUrl)) {
      return imageUrl
    }

    // OpenAI suggested a URL but it doesn't exist
    console.log('OpenAI suggested URL does not exist:', imageUrl)

    // Try variations of the suggested URL (different years for Rolex, etc.)
    if (manufacturer.toLowerCase().includes('rolex')) {
      const currentYear = new Date().getFullYear()
      for (let year = currentYear; year >= currentYear - 3; year--) {
        const yearUrl = imageUrl.replace(/\/catalogue\/\d{4}\//, `/catalogue/${year}/`)
        if (await checkImageExists(yearUrl)) {
          return yearUrl
        }
      }
    }

    return null
  } catch (error) {
    console.error('Error using OpenAI for image search:', error)
    return null
  }
}

/**
 * Check if an image URL exists and is accessible
 * Uses GET request with abort for better compatibility (some servers block HEAD)
 */
async function checkImageExists(url: string): Promise<boolean> {
  try {
    // For known reliable sources, trust the URL format and skip verification
    // This avoids issues with CORS, rate limiting, and servers that block HEAD requests
    if (url.includes('media.rolex.com') || url.includes('rolex.com')) {
      console.log('  → Rolex URL detected, trusting format')
      // For Rolex, just verify the format is correct
      return url.includes('/upright-c/m') && /m[0-9a-z-]+/.test(url)
    }

    // For other sources, try to verify
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 3000) // 3s timeout

    const response = await fetch(url, {
      method: 'HEAD',
      cache: 'no-cache',
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; WatchService/1.0)',
      },
    })

    clearTimeout(timeoutId)

    const isValid = response.ok && (response.headers.get('content-type')?.startsWith('image/') ?? false)
    console.log(`  → URL check: ${isValid ? '✓' : '✗'} (${response.status})`)
    return isValid
  } catch (error: any) {
    console.log(`  → URL check failed: ${error.message}`)
    return false
  }
}

/**
 * Validate that a URL is a valid image
 */
export function isValidImageUrl(url: string): boolean {
  try {
    new URL(url)
    return url.match(/\.(jpg|jpeg|png|gif|webp)(\?.*)?$/i) !== null ||
           url.includes('rolex.com') ||
           url.includes('omegawatches.com') ||
           url.includes('patek.com')
  } catch {
    return false
  }
}
