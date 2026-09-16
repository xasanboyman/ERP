import request from '@/axios'
import type { WorkplaceTotal, Project, Dynamic, Team, RadarData } from './types'

export interface WorkplaceSummaryData {
  productsCount: number
  activeWorkersCount: number
  salesCount: number
  debtorsCount: number
  totalDebtAmount: number
}

export const getWorkplaceSummaryApi = (): Promise<IResponse<WorkplaceSummaryData>> => {
  return request.get({ url: '/workplace/summary' })
}

export const getCountApi = (): Promise<IResponse<WorkplaceTotal>> => {
  return request.get({ url: '/mock/workplace/total' })
}

export const getProjectApi = (): Promise<IResponse<Project>> => {
  return request.get({ url: '/mock/workplace/project' })
}

export const getDynamicApi = (): Promise<IResponse<Dynamic[]>> => {
  return request.get({ url: '/mock/workplace/dynamic' })
}

export const getTeamApi = (): Promise<IResponse<Team[]>> => {
  return request.get({ url: '/mock/workplace/team' })
}

export const getRadarApi = (): Promise<IResponse<RadarData[]>> => {
  return request.get({ url: '/mock/workplace/radar' })
}
