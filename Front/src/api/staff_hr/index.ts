import request from '@/axios'

export const getPositionListApi = () => {
  return request.get({ url: '/hr/position/list' })
}

export const savePositionApi = (data: any) => {
  return request.post({ url: '/hr/position/save', data })
}

export const deletePositionApi = (data: { ids: string[] }) => {
  return request.post({ url: '/hr/position/delete', data })
}

export const getAdjustmentListApi = () => {
  return request.get({ url: '/hr/adjustment/list' })
}

export const saveAdjustmentApi = (data: any) => {
  return request.post({ url: '/hr/adjustment/save', data })
}

export const deleteAdjustmentApi = (data: { ids: string[] }) => {
  return request.post({ url: '/hr/adjustment/delete', data })
}

export const getTimesheetListApi = () => {
  return request.get({ url: '/hr/timesheet/list' })
}

export const saveTimesheetApi = (data: any) => {
  return request.post({ url: '/hr/timesheet/save', data })
}

export const deleteTimesheetApi = (data: { ids: string[] }) => {
  return request.post({ url: '/hr/timesheet/delete', data })
}

export const getOutputListApi = () => {
  return request.get({ url: '/hr/output/list' })
}

export const saveOutputApi = (data: any) => {
  return request.post({ url: '/hr/output/save', data })
}

export const deleteOutputApi = (data: { ids: string[] }) => {
  return request.post({ url: '/hr/output/delete', data })
}
