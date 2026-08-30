import request from '@/axios'

export const getRoleListApi = () => {
  return request.get({ url: '/role/table' })
}

export const saveRoleApi = (data: any) => {
  return request.post({ url: '/role/save', data })
}

export const deleteRoleApi = (data: { id: string }) => {
  return request.post({ url: '/role/delete', data })
}
