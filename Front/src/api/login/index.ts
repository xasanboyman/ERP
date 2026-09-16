import request from '@/axios'
import type { UserType } from './types'

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

export const getAdminRoleApi = (): Promise<IResponse<AppCustomRouteRecordRaw[]>> => {
  return request.get({ url: '/role/list' })
}

export const getTestRoleApi = (): Promise<IResponse<string[]>> => {
  return request.get({ url: '/role/list' })
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
