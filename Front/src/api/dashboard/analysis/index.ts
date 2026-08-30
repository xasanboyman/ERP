import request from '@/axios'
import type {
  AnalysisTotalTypes,
  UserAccessSource,
  WeeklyUserActivity,
  MonthlySales
} from './types'

export const getCountApi = (): Promise<IResponse<AnalysisTotalTypes[]>> => {
  return request.get({ url: '/mock/analysis/total' })
}

export const getUserAccessSourceApi = (): Promise<IResponse<UserAccessSource[]>> => {
  return request.get({ url: '/mock/analysis/userAccessSource' })
}

export const getWeeklyUserActivityApi = (): Promise<IResponse<WeeklyUserActivity[]>> => {
  return request.get({ url: '/mock/analysis/weeklyUserActivity' })
}

export const getMonthlySalesApi = (): Promise<IResponse<MonthlySales[]>> => {
  return request.get({ url: '/mock/analysis/monthlySales' })
}

export interface MonthlyFinancialSnapshotItem {
  id: string
  period_month: string
  revenue: number
  cogs: number
  staff_salaries: number
  short_term_outputs: number
  total_expenses: number
  net_profit: number
  profit_margin: number
  sales_count: number
  status: string
  remark?: string
  closed_by?: string
  created_at?: string
}

export const getFinancialSnapshotsApi = (): Promise<IResponse<MonthlyFinancialSnapshotItem[]>> => {
  return request.get({ url: '/analysis/snapshot/list' })
}

export const closeMonthlyFinancialSnapshotApi = (data: {
  period_month: string
  remark?: string
  override_revenue?: number
  override_cogs?: number
  override_staff_salaries?: number
  override_short_term?: number
}): Promise<IResponse<MonthlyFinancialSnapshotItem>> => {
  return request.post({ url: '/analysis/snapshot/close', data })
}

export const deleteFinancialSnapshotApi = (data: {
  id?: string
  period_month?: string
}): Promise<IResponse<any>> => {
  return request.post({ url: '/analysis/snapshot/delete', data })
}
