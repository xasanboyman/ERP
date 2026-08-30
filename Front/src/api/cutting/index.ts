import request from '@/axios'

export const getStageListApi = () => {
  return request.get({ url: '/cutting/stage/list' })
}

export const saveStageApi = (data: any) => {
  return request.post({ url: '/cutting/stage/save', data })
}

export const deleteStageApi = (data: { ids: string[] }) => {
  return request.post({ url: '/cutting/stage/delete', data })
}

export const getProcessListApi = () => {
  return request.get({ url: '/cutting/process/list' })
}

export const saveProcessApi = (data: any) => {
  return request.post({ url: '/cutting/process/save', data })
}

export const deleteProcessApi = (data: { ids: string[] }) => {
  return request.post({ url: '/cutting/process/delete', data })
}

export const getOrderListApi = () => {
  return request.get({ url: '/cutting/order/list' })
}

export const saveOrderApi = (data: any) => {
  return request.post({ url: '/cutting/order/save', data })
}

export const deleteOrderApi = (data: { ids: string[] }) => {
  return request.post({ url: '/cutting/order/delete', data })
}

export const startProductionApi = (data: { orderId: string }) => {
  return request.post({ url: '/cutting/order/start-production', data })
}

export const getTaskListApi = () => {
  return request.get({ url: '/cutting/task/list' })
}

export const updateTaskStatusApi = (data: { taskId: string; status: string }) => {
  return request.post({ url: '/cutting/task/update-status', data })
}

export const getExecutionListApi = () => {
  return request.get({ url: '/cutting/task/execution/list' })
}

export const saveExecutionApi = (data: any) => {
  return request.post({ url: '/cutting/task/execution/save', data })
}

export const deleteExecutionApi = (data: { ids: string[] }) => {
  return request.post({ url: '/cutting/task/execution/delete', data })
}
