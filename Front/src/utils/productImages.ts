import { reactive } from 'vue'

/**
 * Utility functions for generating Tasnif Soliq product image URLs dynamically based on MXIK code.
 * Fetches real picture filenames from Tasnif Soliq API with Vue reactivity & caching.
 */

export const TASNIF_FILE_CDN =
  'https://tasnif.soliq.uz/api/cls-api/integration-mxik/references/get/file/'
export const TASNIF_PICS_API =
  'https://tasnif.soliq.uz/api/cls-api/integration-mxik/references/get/mxik/picture-names?mxik_code='

export const getTasnifFileUrl = (fileName: string): string => {
  if (!fileName) return ''
  return fileName.startsWith('http') ? fileName : `${TASNIF_FILE_CDN}${fileName}`
}

export const getProductInitials = (productName?: string): string => {
  if (!productName || !productName.trim()) return '?'
  const parts = productName
    .trim()
    .split(/[\s,._-]+/)
    .filter(Boolean)
  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[1][0]).toUpperCase()
}

// Vue reactive in-memory cache for picture name arrays per MXIK code
const pictureCache = reactive<Record<string, string[]>>({})
const fetchingSet = new Set<string>()

/**
 * Asynchronously fetch real picture names from Tasnif API for a given MXIK code
 */
export const fetchTasnifPictureNames = async (mxikCode: string): Promise<string[]> => {
  if (!mxikCode) return []
  const mxik = mxikCode.trim()
  if (pictureCache[mxik] !== undefined) {
    return pictureCache[mxik]
  }

  if (fetchingSet.has(mxik)) {
    return []
  }
  fetchingSet.add(mxik)

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 6000) // 6 sec timeout safeguard

    const res = await fetch(`${TASNIF_PICS_API}${mxik}`, { signal: controller.signal })
    clearTimeout(timeoutId)

    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data) && data.length > 0) {
        pictureCache[mxik] = data
        fetchingSet.delete(mxik)
        return data
      }
    }
  } catch (e) {
    console.warn(`[Tasnif API] Picture fetch failed for ${mxik}:`, e)
  }

  // Mark as empty array so we don't spam repeat requests or generate fake 404 URLs
  pictureCache[mxik] = []
  fetchingSet.delete(mxik)
  return []
}

/**
 * Main product image URL getter with Vue reactivity.
 * Shows custom image_url if set, or real Tasnif picture if cached/loaded, or initial avatar fallback.
 */
export const getProductMainImage = (row?: {
  image_url?: string
  mxik_code?: string
  productName?: string
  name?: string
}): string => {
  if (!row) return ''

  // 1. Custom uploaded product image
  if (row.image_url && row.image_url.trim()) {
    const url = row.image_url.trim()
    if (!url.startsWith('http') && !url.startsWith('/')) {
      return `/${url}`
    }
    return url
  }

  // 2. Tasnif Soliq real image by MXIK code
  if (row.mxik_code && row.mxik_code.trim()) {
    const mxik = row.mxik_code.trim()
    const cached = pictureCache[mxik]

    if (cached !== undefined) {
      if (cached.length > 0) {
        const pic = cached[0]
        return pic.startsWith('http') ? pic : `${TASNIF_FILE_CDN}${pic}`
      }
    } else {
      // Trigger background async fetch
      fetchTasnifPictureNames(mxik)
    }
  }

  // 3. Initials Avatar Fallback
  return getProductFallbackAvatar(row.productName || row.name)
}

/**
 * Synchronous getter for full product image gallery array.
 */
export const getProductImageGallery = (row?: {
  image_url?: string
  mxik_code?: string
}): string[] => {
  if (!row) return []
  const list: string[] = []

  if (row.image_url && row.image_url.trim()) {
    const url = row.image_url.trim()
    list.push(url.startsWith('http') || url.startsWith('/') ? url : `/${url}`)
  }

  if (row.mxik_code && row.mxik_code.trim()) {
    const mxik = row.mxik_code.trim()
    const cached = pictureCache[mxik]

    if (cached !== undefined && cached.length > 0) {
      cached.forEach((pic) => {
        const fullUrl = pic.startsWith('http') ? pic : `${TASNIF_FILE_CDN}${pic}`
        if (!list.includes(fullUrl)) {
          list.push(fullUrl)
        }
      })
    } else if (cached === undefined) {
      fetchTasnifPictureNames(mxik)
    }
  }
  return list
}

/**
 * Fallback avatar URL generated from product name
 */
export const getProductFallbackAvatar = (productName?: string): string => {
  const name = (productName || 'Product').trim()
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=1e293b&color=38bdf8&size=128&bold=true&font-size=0.4`
}

/**
 * Image error handler that swaps broken src to clean UI avatar
 */
export const handleImageError = (e: Event, productName?: string) => {
  const target = e.target as HTMLImageElement
  if (target) {
    target.onerror = null // Prevent infinite error loops
    target.src = getProductFallbackAvatar(productName)
  }
}
