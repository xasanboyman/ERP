import request from '@/axios'

export interface ProductPackagingType {
  id?: string
  product_id?: string
  unit_name: string
  conversion_factor: number
  price: number
  cost?: number
  shtrix_code?: string
  is_base_unit?: boolean
}

export interface ProductType {
  id?: string
  productName: string
  SKU: string
  category: string
  price: number
  cost: number
  quantityInStock: number
  status?: number
  classifier_id?: number
  shtrix_code?: string
  mxik_code?: string
  brand_name?: string
  attribute_name?: string
  unit?: string
  image_url?: string
  expiration_date?: string
  remark?: string
  createTime?: string
  packagings?: ProductPackagingType[]
  selected_packaging?: ProductPackagingType
}

export const getProductListApi = (params: any) => {
  return request.get<{
    list: ProductType[]
    total: number
  }>({ url: '/product/list', params })
}

export const saveProductApi = (data: ProductType) => {
  return request.post({ url: '/product/save', data })
}

export const deleteProductApi = (data: { ids: string[] }) => {
  return request.post({ url: '/product/delete', data })
}

export const uploadProductImageApi = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<{ url: string }>({
    url: '/product/upload-image',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const searchClassifierApi = async (params: {
  search?: string
  brand?: string
  mxik_code?: string
  shtrix_code?: string
  page?: number
  page_size?: number
  mode?: 'extended' | 'simple' | 'local' | string
  lang?: string
}) => {
  const cleanQ = (params.search || '').trim()
  const page = params.page || 1
  const pageSize = params.page_size || 25
  const mode = params.mode || 'extended'
  const lang = params.lang || 'uz_latn'

  // Direct Tasnif Soliq Elasticsearch fetch from client browser (runs in ~100-200ms with CORS!)
  if (cleanQ && mode === 'extended' && typeof window !== 'undefined') {
    try {
      const pZero = Math.max(0, page - 1)
      const url = `https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?lang=${encodeURIComponent(lang)}&search=${encodeURIComponent(cleanQ)}&size=${pageSize}&page=${pZero}`
      const controller = new AbortController()
      const tId = setTimeout(() => controller.abort(), 4000)
      const resp = await fetch(url, { signal: controller.signal })
      clearTimeout(tId)
      if (resp.ok) {
        const json = await resp.json()
        if (json && json.success && Array.isArray(json.data) && json.data.length > 0) {
          const list = json.data.map((item: any, idx: number) => ({
            id:
              item.mxikCode ||
              (item.internationalCode ? `bar_${item.internationalCode}` : `ext_${page}_${idx}`),
            mxik_code: item.mxikCode || '',
            mxik_name: item.name || '',
            brand_name: item.brandName || '',
            attribute_name: item.attributeName || '',
            shtrix_code: item.internationalCode || '',
            unit: item.unitsName || 'dona',
            group_name: item.groupName || '',
            group_code: item.groupCode || '',
            class_name: item.className || '',
            position_name: item.positionName || '',
            subposition_name: item.subPositionName || '',
            category_name: item.categoryName || '',
            search_mode: 'extended'
          }))
          return {
            code: 0,
            data: list,
            list,
            total: json.recordTotal || list.length,
            page,
            page_size: pageSize
          } as any
        }
      }
    } catch (clientErr) {
      console.warn('Client-side Tasnif fetch failed, falling back to server router:', clientErr)
    }
  }

  return request.get<{
    code: number
    data: any[]
    total: number
    page: number
    page_size: number
  }>({ url: '/classifier/list', params })
}

export const getClassifierByBarcodeApi = async (barcode: string) => {
  const cleanCode = (barcode || '').trim()
  if (cleanCode && typeof window !== 'undefined') {
    try {
      const url = `https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?lang=uz_latn&search=${encodeURIComponent(cleanCode)}&size=5&page=0`
      const controller = new AbortController()
      const tId = setTimeout(() => controller.abort(), 4000)
      const resp = await fetch(url, { signal: controller.signal })
      clearTimeout(tId)
      if (resp.ok) {
        const json = await resp.json()
        if (json && json.success && Array.isArray(json.data) && json.data.length > 0) {
          const exact =
            json.data.find((d: any) => d.internationalCode === cleanCode) || json.data[0]
          return {
            data: {
              id: exact.mxikCode || cleanCode,
              mxik_code: exact.mxikCode || '',
              mxik_name: exact.name || '',
              brand_name: exact.brandName || '',
              attribute_name: exact.attributeName || '',
              shtrix_code: exact.internationalCode || cleanCode,
              unit: exact.unitsName || 'dona',
              group_name: exact.groupName || '',
              class_name: exact.className || '',
              position_name: exact.positionName || '',
              subposition_name: exact.subPositionName || '',
              source: 'tasnif_elasticsearch'
            }
          } as any
        }
      }
    } catch (e) {}
  }

  return request.get<{
    data: any
  }>({ url: `/classifier/by-barcode/${barcode}` })
}

export const getProductByBarcodeApi = (barcode: string) => {
  return request.get<{
    code: number
    data: ProductType
  }>({ url: `/api/product/by-barcode/${encodeURIComponent(barcode)}` })
}
