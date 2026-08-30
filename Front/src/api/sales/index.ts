import request from '@/axios'

export interface SaleItemType {
  id?: string
  product_id: string
  product_name: string
  shtrix_code?: string
  price: number
  cost?: number
  quantity: number
  unit_name?: string
  conversion_factor?: number
  total?: number
}

export interface SaleType {
  id?: string
  receipt_number?: string
  cashier_name?: string
  customer_name?: string
  customer_phone?: string
  payment_method?: 'naqd' | 'karta' | 'otkazma' | 'nasiya'
  total_amount?: number
  paid_amount?: number
  debt_amount?: number
  total_items?: number
  discount?: number
  remark?: string
  created_at?: string
  items: SaleItemType[]
}

export const getSalesListApi = (params: {
  pageIndex: number
  pageSize: number
  search?: string
  payment_method?: string
  cashier_name?: string
}) => {
  return request.get({ url: '/sales/list', params })
}

export const checkoutSaleApi = (data: SaleType) => {
  return request.post({ url: '/sales/checkout', data })
}

export const getDebtorsApi = (params?: { search?: string; status?: string }) => {
  return request.get({ url: '/sales/debtors', params })
}

export const getDebtorDetailApi = (name: string) => {
  return request.get({ url: '/sales/debtor-detail', params: { name } })
}

export const repayDebtApi = (data: {
  customer_name: string
  customer_phone?: string
  amount: number
  payment_method?: string
  cashier_name?: string
  remark?: string
}) => {
  return request.post({ url: '/sales/repay-debt', data })
}

export const getSaleReceiptApi = (receipt_number: string) => {
  return request.get({ url: `/sales/receipt/${receipt_number}` })
}

export const getPaymentReceiptApi = (receipt_number: string) => {
  return request.get({ url: `/sales/payment-receipt/${receipt_number}` })
}
