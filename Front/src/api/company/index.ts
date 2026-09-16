import request from '@/axios'

export interface CompanyType {
  id?: string
  name: string
  code: string
  plan: 'basic' | 'pro'
  billing_cycle: 'monthly' | 'yearly'
  subscription_expires_at?: string
  status: number
  max_users?: number
  phone?: string
  email?: string
  address?: string
  features?: {
    ai?: boolean
    upcoming?: boolean
    advanced_analytics?: boolean
    [key: string]: any
  }
  created_at?: string
  employees_count?: number
  workers_count?: number
  users_count?: number
  products_count?: number
  total_sales_count?: number
  total_revenue?: number
  is_expired?: boolean
  admin_username?: string
  admin_password?: string
  admin_full_name?: string
}

export interface CompanyWorkerType {
  id: string
  name: string
  role?: string
  phone?: string
  account?: string
  employee_code?: string
  department?: string
  hireDate?: string
  status?: number
  baseSalary?: number
  company_id?: string
}

export interface CompanyDetailType extends CompanyType {
  usage_percent?: number
  stats: {
    employees_count: number
    workers_count: number
    users_count: number
    max_users: number
    usage_percent: number
    products_count: number
    total_stock: number
    inventory_value: number
    total_sales_count: number
    total_revenue: number
    total_sales_amount: number
    total_debt: number
    debtors_count: number
  }
  workers: CompanyWorkerType[]
  users: Array<{
    id: number
    username: string
    full_name?: string
    role?: string
    email?: string
    phone?: string
    company_id?: string
  }>
  recent_sales: Array<{
    id: string
    customer_name?: string
    customer_phone?: string
    total_amount: number
    paid_amount: number
    debt_amount: number
    createTime?: string
  }>
  top_products: Array<{
    id: string
    productName: string
    category?: string
    price: number
    stock: number
    unit?: string
  }>
}

export const getCompanyListApi = (params?: any) => {
  return request.get<{
    list: CompanyType[]
    total: number
  }>({ url: '/company/list', params })
}

export const getCurrentCompanyApi = () => {
  return request.get<{
    company_id: string
    name: string
    code: string
    plan: 'basic' | 'pro'
    billing_cycle: 'monthly' | 'yearly'
    subscription_expires_at?: string
    status: number
    features: Record<string, any>
    is_super_admin: boolean
  }>({ url: '/company/current' })
}

export const getCompanyDetailApi = (companyId: string) => {
  return request.get<CompanyDetailType>({ url: `/company/detail/${companyId}` })
}

export const saveCompanyApi = (data: Partial<CompanyType>) => {
  return request.post({ url: '/company/save', data })
}

export const updateCompanyTierApi = (data: {
  company_id: string
  plan: 'basic' | 'pro'
  billing_cycle?: 'monthly' | 'yearly'
  duration_months?: number
  subscription_expires_at?: string
  max_users?: number
  features?: Record<string, any>
}) => {
  return request.post({ url: '/company/tier', data })
}

export const toggleCompanyStatusApi = (data: { company_id: string; status: number }) => {
  return request.post({ url: '/company/status', data })
}

export const deleteCompanyApi = (data: { id: string }) => {
  return request.post({ url: '/company/delete', data })
}

export const saveCompanyEmployeeApi = (data: {
  id?: string
  company_id: string
  name: string
  role?: string
  phone?: string
  account?: string
  employee_code?: string
  department?: string
  hireDate?: string
  status?: number
  baseSalary?: number
}) => {
  return request.post({ url: '/company/employee/save', data })
}

export const deleteCompanyEmployeeApi = (data: { id: string; company_id: string }) => {
  return request.post({ url: '/company/employee/delete', data })
}

export const getMainAccountApi = () => {
  return request.get<{
    super_admin: {
      id: number
      username: string
      full_name: string
      email: string
      phone: string
    }
    main_company: {
      id: string
      name: string
      code: string
      plan: string
      billing_cycle: string
      max_users: number
      phone: string
      email: string
      address: string
    }
  }>({ url: '/company/main-account' })
}

export const updateMainAccountApi = (data: {
  company_name?: string
  company_code?: string
  company_phone?: string
  company_email?: string
  company_address?: string
  admin_username?: string
  admin_password?: string
  admin_full_name?: string
  admin_email?: string
  admin_phone?: string
}) => {
  return request.post({ url: '/company/main-account', data })
}

export const resetCompanyPasswordApi = (data: {
  company_id: string
  new_password: string
  username?: string
  full_name?: string
}) => {
  return request.post({ url: '/company/account/reset-password', data })
}

