import request from '@/axios'

export interface WorkerType {
  id?: string
  name: string
  account: string
  email?: string
  phone?: string
  role?: string
  departmentId?: string
  departmentName?: string
  hireDate?: string
  status?: number
  baseSalary?: number
  remark?: string
  password?: string
  adminPassword?: string
}

export const getWorkerListApi = (params: any) => {
  return request.get<{
    list: WorkerType[]
    total: number
  }>({ url: '/worker/list', params })
}

export const saveWorkerApi = (data: WorkerType) => {
  return request.post({ url: '/worker/save', data })
}

export const deleteWorkerApi = (data: { ids: string[] }) => {
  return request.post({ url: '/worker/delete', data })
}
