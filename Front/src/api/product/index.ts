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

export const searchClassifierApi = (params: {
  search?: string
  brand?: string
  mxik_code?: string
  shtrix_code?: string
  page?: number
  page_size?: number
}) => {
  return request.get<{
    code: number
    data: any[]
    total: number
    page: number
    page_size: number
  }>({ url: '/classifier/list', params })
}

export const getClassifierByBarcodeApi = (barcode: string) => {
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
