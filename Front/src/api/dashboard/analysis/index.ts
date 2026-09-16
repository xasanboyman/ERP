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

export interface MonthlyFinancialItem {
  month: string
  period_month: string
  revenue: number
  cogs: number
  staffSalaries: number
  shortTermOutputs: number
  totalPayroll: number
  totalExpenses: number
  netProfit: number
  profitMargin: number
  salesCount: number
}

export interface FinancialOverviewData {
  grossRevenue: number
  cogs: number
  staffSalaries: number
  shortTermOutputs: number
  totalPayroll: number
  totalExpenses: number
  realNetProfit: number
  profitMargin: number
  activeWorkersCount: number
  shortTermTasksCount: number
  monthlyFinancials: MonthlyFinancialItem[]
  expenseBreakdown: Array<{ name: string; value: number }>
  categoryProfits: Array<{ name: string; revenue: number; cost: number; profit: number }>
}

export interface MonthSummaryData {
  period_month: string
  revenue: number
  cogs: number
  staffSalaries: number
  shortTermOutputs: number
  totalPayroll: number
  totalExpenses: number
  netProfit: number
  profitMargin: number
  salesCount: number
  is_frozen: boolean
  status?: string
  remark?: string
  closed_by?: string
  created_at?: string
}

export interface PeriodComparisonData {
  period1: {
    start_date: string
    end_date: string
    revenue: number
    cogs: number
    staff_salaries: number
    short_term_outputs: number
    total_payroll: number
    total_expenses: number
    net_profit: number
    profit_margin: number
    sales_count: number
  }
  period2: {
    start_date: string
    end_date: string
    revenue: number
    cogs: number
    staff_salaries: number
    short_term_outputs: number
    total_payroll: number
    total_expenses: number
    net_profit: number
    profit_margin: number
    sales_count: number
  }
  deltas: {
    revDiff: number
    revGrowth: number
    cogsDiff: number
    cogsGrowth: number
    staffDiff: number
    staffGrowth: number
    shortDiff: number
    shortGrowth: number
    payrollDiff: number
    payrollGrowth: number
    profitDiff: number
    profitGrowth: number
    marginDiff: number
  }
}

export const getFinancialOverviewApi = (params?: {
  time_range?: string
}): Promise<IResponse<FinancialOverviewData>> => {
  return request.get({ url: '/analysis/financial-overview', params })
}

export const getMonthSummaryApi = (params: {
  month: string
}): Promise<IResponse<MonthSummaryData>> => {
  return request.get({ url: '/analysis/month-summary', params })
}

export const comparePeriodsApi = (data: {
  period1_start: string
  period1_end: string
  period2_start: string
  period2_end: string
}): Promise<IResponse<PeriodComparisonData>> => {
  return request.post({ url: '/analysis/compare', data })
}

export const getDateRangeAnalysisApi = (params: {
  start_date: string
  end_date: string
}): Promise<IResponse<any>> => {
  return request.get({ url: '/analysis/date-range', params })
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

export interface AnalysisBundleData {
  overview: FinancialOverviewData
  snapshots: MonthlyFinancialSnapshotItem[]
  monthSummary: MonthSummaryData
  comparison: PeriodComparisonData
}

export const getAnalysisBundleApi = (params?: {
  time_range?: string
  month?: string
  p1_start?: string
  p1_end?: string
  p2_start?: string
  p2_end?: string
}): Promise<IResponse<AnalysisBundleData>> => {
  return request.get({ url: '/analysis/bundle', params })
}
