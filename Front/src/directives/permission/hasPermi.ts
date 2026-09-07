import type { App, Directive, DirectiveBinding } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import router from '@/router'

const { t } = useI18n()

import { useUserStoreWithOut } from '@/store/modules/user'

const hasPermission = (value: string | string[]): boolean => {
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
function hasPermi(el: Element, binding: DirectiveBinding) {
  const value = binding.value

  const flag = hasPermission(value)
  if (!flag) {
    el.parentNode?.removeChild(el)
  }
}
const mounted = (el: Element, binding: DirectiveBinding<any>) => {
  hasPermi(el, binding)
}

const permiDirective: Directive = {
  mounted
}

export const setupPermissionDirective = (app: App<Element>) => {
  app.directive('hasPermi', permiDirective)
}

export default permiDirective
