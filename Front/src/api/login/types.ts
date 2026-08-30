export interface UserLoginType {
  username: string
  password: string
}

export interface UserType {
  id?: number | string
  username: string
  password?: string
  full_name?: string
  role?: string
  roleId?: string
  avatar?: string
  token?: string
}
