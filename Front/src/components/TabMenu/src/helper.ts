import { getAllParentPath } from '@/components/Menu/src/helper'
import { isUrl } from '@/utils/is'
import { cloneDeep } from 'lodash-es'
import { reactive } from 'vue'

export type TabMapTypes = {
  [key: string]: string[]
}

export const tabPathMap = reactive<TabMapTypes>({})

export const initTabMap = (routes: AppRouteRecordRaw[]) => {
  if (!routes || !Array.isArray(routes)) return
  for (const v of routes) {
    if (!v) continue
    const meta = v.meta ?? {}
    if (!meta?.hidden && v.path) {
      tabPathMap[v.path] = []
    }
  }
}

export const filterMenusPath = (
  routes: AppRouteRecordRaw[],
  allRoutes: AppRouteRecordRaw[]
): AppRouteRecordRaw[] => {
  const res: AppRouteRecordRaw[] = []
  if (!routes || !Array.isArray(routes)) return res
  const safeAllRoutes = Array.isArray(allRoutes) ? allRoutes : []

  for (const v of routes) {
    if (!v) continue
    let data: Nullable<AppRouteRecordRaw> = null
    const meta = v.meta ?? {}
    if (!meta.hidden || meta.canTo) {
      const allParentPath = getAllParentPath<AppRouteRecordRaw>(safeAllRoutes, v.path || '')

      const fullPath = isUrl(v.path || '') ? v.path : allParentPath.join('/')

      data = cloneDeep(v)
      data.path = fullPath
      if (v.children && data && Array.isArray(v.children)) {
        data.children = filterMenusPath(v.children, safeAllRoutes)
      }

      if (data) {
        res.push(data)
      }

      if (allParentPath.length && Reflect.has(tabPathMap, allParentPath[0])) {
        if (!Array.isArray(tabPathMap[allParentPath[0]])) {
          tabPathMap[allParentPath[0]] = []
        }
        tabPathMap[allParentPath[0]].push(fullPath)
      }
    }
  }

  return res
}
