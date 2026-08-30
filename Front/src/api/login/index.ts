import request from '@/axios'
import type { UserType } from './types'

interface RoleParams {
  roleName: string
}

export const loginApi = (data: UserType): Promise<IResponse<UserType>> => {
  return request.post({ url: '/user/login', data })
}

export const loginOutApi = (): Promise<IResponse> => {
  return request.get({ url: '/user/loginOut' })
}

export const getEmployeesAuthApi = (): Promise<IResponse<any[]>> => {
  return request.get({ url: '/user/employees' })
}

export const getUserListApi = ({ params }: AxiosConfig) => {
  return request.get<{
    code: string
    data: {
      list: UserType[]
      total: number
    }
  }>({ url: '/user/list', params })
}

export const getAdminRoleApi = (
  params: RoleParams
): Promise<IResponse<AppCustomRouteRecordRaw[]>> => {
  return request.get({ url: '/role/list', params })
}

export const getTestRoleApi = (params: RoleParams): Promise<IResponse<string[]>> => {
  return request.get({ url: '/role/list2', params })
}

export const updateUserAvatarApi = (data: {
  username: string
  avatar?: string
  full_name?: string
}): Promise<IResponse<UserType>> => {
  return request.post({ url: '/user/avatar', data })
}

export const saveUserApi = (data: any): Promise<IResponse<UserType>> => {
  return request.post({ url: '/user/save', data })
}
