import request from '@/axios'

export interface SalaryType {
  id?: string
  workerId: string
  workerName?: string
  departmentName?: string
  baseSalary: number
  allowance: number
  deduction: number
  netSalary?: number
  payDate?: string
  status?: string
  remark?: string
}

export const getSalaryListApi = (params: any) => {
  return request.get<{
    list: SalaryType[]
    total: number
  }>({ url: '/salary/list', params })
}

export const saveSalaryApi = (data: SalaryType) => {
  return request.post({ url: '/salary/save', data })
}

export const deleteSalaryApi = (data: { ids: string[] }) => {
  return request.post({ url: '/salary/delete', data })
}

export interface SalaryPayoutItem {
  workerId: string
  baseSalary?: number
  allowance?: number
  deduction?: number
  period_month?: string
  remark?: string
}

export const bulkSalaryPayoutApi = (data: {
  workerIds?: string[]
  items?: SalaryPayoutItem[]
  period_month?: string
  allowance?: number
  deduction?: number
  remark?: string
}) => {
  return request.post({ url: '/salary/payout', data })
}
