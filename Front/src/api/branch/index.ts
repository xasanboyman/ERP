import request from '@/axios'

export interface BranchType {
  id?: string
  name: string
  code?: string
  address?: string
  phone?: string
  is_active?: number
}

export const getBranchListApi = () => {
  return request.get<{ code: number; data: BranchType[] }>({
    url: '/branch/list'
  })
}

export const saveBranchApi = (data: BranchType) => {
  return request.post<{ code: number; message: string; data: BranchType }>({
    url: '/branch/save',
    data
  })
}

export const deleteBranchApi = (id: string) => {
  return request.post<{ code: number; message: string }>({
    url: '/branch/delete',
    data: { id }
  })
}

export interface BranchWorkerItem {
  id: string
  name: string
  role: string
  phone: string
  baseSalary: number
  status: number
}

export interface BranchProductItem {
  id: string
  productName: string
  category: string
  price: number
  quantityInStock: number
  unit: string
}

export interface BranchSaleItem {
  id: string
  receipt_number: string
  total_amount: number
  payment_method: string
  created_at: string
}

export interface BranchStatistics {
  employees: {
    count: number
    active_count: number
    total_salary: number
    list: BranchWorkerItem[]
  }
  products: {
    count: number
    total_quantity: number
    total_inventory_value: number
    low_stock_count: number
    list: BranchProductItem[]
  }
  income: {
    total_revenue: number
    total_sales_count: number
    total_paid: number
    total_debt: number
    average_check: number
    recent_sales: BranchSaleItem[]
  }
}

export interface BranchWithStats extends BranchType {
  company_id?: string
  statistics: BranchStatistics
}

export const getBranchStatisticsApi = (params?: { branch_id?: string; company_id?: string }) => {
  return request.get<{ code: number; data: BranchWithStats[] }>({
    url: '/branch/statistics',
    params
  })
}

