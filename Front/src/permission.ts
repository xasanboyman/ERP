import router from './router'
import { useAppStoreWithOut } from '@/store/modules/app'
import type { RouteRecordRaw } from 'vue-router'
import { useTitle } from '@/hooks/web/useTitle'
import { useNProgress } from '@/hooks/web/useNProgress'
import { usePermissionStoreWithOut } from '@/store/modules/permission'
import { usePageLoading } from '@/hooks/web/usePageLoading'
import { NO_REDIRECT_WHITE_LIST } from '@/constants'
import { useUserStoreWithOut } from '@/store/modules/user'
import { preloadAllViewsAndData } from '@/utils/routerHelper'
import { getAdminRoleApi } from '@/api/login'

const { start, done } = useNProgress()

const { loadStart, loadDone } = usePageLoading()

function isTokenExpired(token?: string): boolean {
  if (!token) return false
  try {
    const cleanToken = token.startsWith('Bearer ') ? token.slice(7) : token
    const parts = cleanToken.split('.')
    if (parts.length !== 3) return false
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    if (payload && payload.exp) {
      return Date.now() >= payload.exp * 1000
    }
  } catch (e) {
    return false
  }
  return false
}

function getFirstRoutePath(routes: any[]): string {
  if (!routes || routes.length === 0) return '/login'
  for (const route of routes) {
    if (route.meta?.hidden) continue
    if (route.children && route.children.length > 0) {
      for (const child of route.children) {
        if (child.meta?.hidden) continue
        const parentPath = route.path.startsWith('/') ? route.path : `/${route.path}`
        const childPath = child.path.startsWith('/') ? child.path : `/${child.path}`
        return parentPath === '/' ? childPath : `${parentPath}/${childPath}`.replace(/\/+/g, '/')
      }
    } else if (route.path) {
      return route.path.startsWith('/') ? route.path : `/${route.path}`
    }
  }
  return '/login'
}

function extractAllRoutePaths(routes: any[], parent = ''): string[] {
  let result: string[] = []
  for (const r of routes) {
    if (!r.path || r.meta?.hidden) continue
    const full = r.path.startsWith('/')
      ? r.path
      : `${parent}/${r.path}`.replace(/\/+/g, '/')
    result.push(full.toLowerCase().replace(/\/$/, ''))
    if (r.children && r.children.length > 0) {
      result = result.concat(extractAllRoutePaths(r.children, full))
    }
  }
  return result
}

router.beforeEach(async (to, from, next) => {
  start()
  loadStart()
  const permissionStore = usePermissionStoreWithOut()
  const appStore = useAppStoreWithOut()
  const userStore = useUserStoreWithOut()

  if (userStore.getToken && isTokenExpired(userStore.getToken)) {
    userStore.logout()
    next(`/login?redirect=${to.path}`)
    return
  }

  if (userStore.getUserInfo) {
    if (to.path === '/login') {
      next({ path: '/' })
      return
    }

    const user = userStore.getUserInfo
    if (user && !user.role) {
      user.role = user.username === 'admin' ? 'Super Administrator' : 'Oddiy xodim'
    }
    const role = (user?.role || '').toLowerCase()
    const isSuper =
      user?.is_super_admin === true ||
      role === 'super administrator' ||
      role === 'superadmin' ||
      user?.username === 'admin'

    // If not super admin, strictly block access to company management under all conditions
    if (!isSuper && to.path.toLowerCase().startsWith('/company')) {
      next({ path: '/404', replace: true })
      return
    }

    if (permissionStore.getIsAddRouters) {
      // If not super admin, check if path is authorized
      if (!isSuper) {
        const allowedPaths = extractAllRoutePaths(permissionStore.getRouters)
        const targetPath = to.path.toLowerCase().replace(/\/$/, '')
        const isAllowed =
          targetPath === '' ||
          targetPath === '/' ||
          targetPath === '/404' ||
          targetPath === '/login' ||
          targetPath === '/redirect' ||
          allowedPaths.includes(targetPath) ||
          allowedPaths.some((p) => p !== '' && p !== '/' && targetPath.startsWith(p + '/'))

        if (!isAllowed) {
          const firstPath = getFirstRoutePath(permissionStore.getAddRouters)
          if (firstPath && firstPath !== to.path && firstPath !== '/login') {
            next({ path: firstPath, replace: true })
            return
          }
        }
      }

      // If navigating to root '/' or an unpermitted route that has no match:
      const matched = router.resolve(to.path).matched
      if (
        to.path === '/' ||
        !matched ||
        matched.length === 0 ||
        matched.some((m) => m.name === 'NoFind')
      ) {
        const firstPath = getFirstRoutePath(permissionStore.getAddRouters)
        if (firstPath && firstPath !== to.path && firstPath !== '/login') {
          next({ path: firstPath, replace: true })
          return
        }
      }
      next()
      return
    }

    let roleRouters: any = userStore.getRoleRouters
    if (!roleRouters || (Array.isArray(roleRouters) && roleRouters.length === 0)) {
      try {
        const res = await getAdminRoleApi()
        if (res && res.data) {
          roleRouters = Array.isArray(res.data) ? res.data : (res.data as any).list || []
          userStore.setRoleRouters(roleRouters)
        }
      } catch (e) {
        console.warn('Failed to fetch role routers on reload:', e)
      }
    }

    if (!Array.isArray(roleRouters)) {
      if (roleRouters && typeof roleRouters === 'object' && Array.isArray(roleRouters.list)) {
        roleRouters = roleRouters.list
      } else {
        roleRouters = []
      }
    }

    if (appStore.getDynamicRouter && roleRouters.length > 0) {
      appStore.serverDynamicRouter
        ? await permissionStore.generateRoutes('server', roleRouters as AppCustomRouteRecordRaw[])
        : await permissionStore.generateRoutes('frontEnd', roleRouters as string[])
    } else if (isSuper) {
      await permissionStore.generateRoutes('static')
    } else {
      await permissionStore.generateRoutes('frontEnd', [
        '/sales',
        '/sales/pos',
        '/product',
        '/product/list'
      ])
    }

      permissionStore.getAddRouters.forEach((route) => {
        router.addRoute(route as unknown as RouteRecordRaw)
      })
      permissionStore.setIsAddRouters(true)

      const rawRedirect = from.query.redirect || to.path
      let decodedRedirect = decodeURIComponent(rawRedirect as string)
      if (!isSuper && decodedRedirect.toLowerCase().startsWith('/company')) {
        decodedRedirect = '/404'
      }
      const matched = router.resolve(decodedRedirect).matched
      const isValidRedirect =
        matched &&
        matched.length > 0 &&
        !matched.some((m) => m.name === 'NoFind') &&
        decodedRedirect !== '/'

      const targetPath = isValidRedirect
        ? decodedRedirect
        : getFirstRoutePath(permissionStore.getAddRouters)
      next({ path: targetPath, replace: true })
  } else {
    if (NO_REDIRECT_WHITE_LIST.indexOf(to.path) !== -1 || to.path.startsWith('/mobile')) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

router.afterEach((to) => {
  useTitle(to?.meta?.title as string)
  done() // 结束Progress
  loadDone()
  preloadAllViewsAndData()
})
