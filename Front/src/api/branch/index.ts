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
