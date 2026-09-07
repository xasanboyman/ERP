import router from '@/router'
import { useUserStoreWithOut } from '@/store/modules/user'

export const hasPermi = (value: string | string[]) => {
  if (!value || (Array.isArray(value) && value.length === 0)) {
    return true
  }
  const userStore = useUserStoreWithOut()
  const role = (userStore.getUserInfo?.role || '').toLowerCase()
  if (role.includes('admin') || role.includes('super')) {
    return true
  }

  const userPerms = (userStore.getUserInfo?.permissions || []) as string[]
  if (userPerms.includes('*.*.*') || userPerms.includes('*')) {
    return true
  }

  const checkList = Array.isArray(value) ? value : [value]
  const hasUserPerm = checkList.some((v) => userPerms.includes(v))
  if (hasUserPerm) return true

  const routePerms = (router.currentRoute.value.meta?.permission || []) as string[]
  return checkList.some((v) => routePerms.includes(v))
}
