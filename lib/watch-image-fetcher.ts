/**
 * Watch Image Fetcher
 * Automatically fetches official product images from manufacturer websites
 */

interface WatchImageParams {
  manufacturer: string
  model: string
  referenceNumber?: string
}

/**
 * Attempts to fetch the official product image from the manufacturer's website
 */
export async function fetchWatchImage(params: WatchImageParams): Promise<string | null> {
  const { manufacturer, model, referenceNumber } = params

  // Normalize manufacturer name
  const normalizedManufacturer = manufacturer.toLowerCase().trim()

  try {
    // Try manufacturer-specific fetchers
    if (normalizedManufacturer.includes('rolex')) {
      return await fetchRolexImage(referenceNumber || '', model)
    }

    if (normalizedManufacturer.includes('omega')) {
      return await fetchOmegaImage(referenceNumber || '', model)
    }

    if (normalizedManufacturer.includes('patek') || normalizedManufacturer.includes('philippe')) {
      return await fetchPatekPhilippeImage(referenceNumber || '', model)
    }

    if (normalizedManufacturer.includes('audemars') || normalizedManufacturer.includes('piguet')) {
      return await fetchAudemarsPiguetImage(referenceNumber || '', model)
    }

    if (normalizedManufacturer.includes('iwc')) {
      return await fetchIWCImage(referenceNumber || '', model)
    }

    // Add more manufacturers as needed

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

  // Remove any dashes or spaces from reference number
  const cleanRef = referenceNumber.replace(/[-\s]/g, '')

  // Try current year and previous years (Rolex updates their catalogue annually)
  const currentYear = new Date().getFullYear()
  const years = [currentYear, currentYear - 1, currentYear - 2, 2024, 2023]

  for (const year of years) {
    // Rolex pattern: m + reference number (e.g., m126710blro-0001)
    const imageUrl = `https://media.rolex.com/image/upload/q_auto:eco/f_auto/t_v7-majesty/c_limit,w_1200/v1/catalogue/${year}/upright-c/m${cleanRef.toLowerCase()}`

    // Check if image exists
    if (await checkImageExists(imageUrl)) {
      return imageUrl
    }
  }

  // Fallback: Try without year in path (older Rolex images)
  const fallbackUrl = `https://content.rolex.com/dam/new-watches-2024/configure-hub/m${cleanRef.toLowerCase()}/1-configure/configure-2024-${model.toLowerCase().replace(/\s+/g, '-')}-m${cleanRef.toLowerCase()}_portrait.png`

  if (await checkImageExists(fallbackUrl)) {
    return fallbackUrl
  }

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
 * Check if an image URL exists and is accessible
 */
async function checkImageExists(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, {
      method: 'HEAD',
      cache: 'no-cache',
    })
    return response.ok && response.headers.get('content-type')?.startsWith('image/')
  } catch {
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
