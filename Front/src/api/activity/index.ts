import request from '@/axios'

export interface ActivityLogType {
  id: number
  actor: string
  action: string // created | updated | deleted | payout
  entity: string // worker | product | salary | department
  entityId?: string
  entityName?: string
  timestamp: string
}

export const getActivityListApi = (params?: { pageSize?: number; pageIndex?: number }) => {
  return request.get<{
    list: ActivityLogType[]
    total: number
  }>({ url: '/activity/list', params })
}
