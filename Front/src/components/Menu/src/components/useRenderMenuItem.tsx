import { ElSubMenu, ElMenuItem } from 'element-plus'
import { unref } from 'vue'
import { hasOneShowingChild } from '../helper'
import { isUrl } from '@/utils/is'
import { useRenderMenuTitle } from './useRenderMenuTitle'
import { pathResolve } from '@/utils/routerHelper'
import { useDesign } from '@/hooks/web/useDesign'

const { getPrefixCls } = useDesign()
const prefixCls = getPrefixCls('submenu')

const { renderMenuTitle } = useRenderMenuTitle()

const prefetchedPaths = new Set<string>()

const prefetchRouteComponent = (targetPath: string) => {
  if (!targetPath || prefetchedPaths.has(targetPath)) return
  prefetchedPaths.add(targetPath)

  try {
    if (targetPath.includes('/product/list')) import('@/views/Product/Product.vue')
    else if (targetPath.includes('/sales/pos')) import('@/views/Sales/Pos.vue')
    else if (targetPath.includes('/sales/debtors')) import('@/views/Sales/Debtors.vue')
    else if (targetPath.includes('/hr/workers')) import('@/views/Worker/Worker.vue')
    else if (targetPath.includes('/hr/salary')) import('@/views/Salary/Salary.vue')
    else if (targetPath.includes('/hr/positions')) import('@/views/StaffHR/Position.vue')
    else if (targetPath.includes('/hr/timesheets')) import('@/views/StaffHR/Timesheet.vue')
    else if (targetPath.includes('/hr/outputs')) import('@/views/StaffHR/Output.vue')
    else if (targetPath.includes('/hr/adjustments')) import('@/views/StaffHR/Adjustment.vue')
    else if (targetPath.includes('/dashboard/analysis')) import('@/views/Dashboard/Analysis.vue')
    else if (targetPath.includes('/dashboard/workplace')) import('@/views/Dashboard/Workplace.vue')
    else if (targetPath.includes('/authorization/role'))
      import('@/views/Authorization/Role/Role.vue')
    else if (targetPath.includes('/authorization/department'))
      import('@/views/Authorization/Department/Department.vue')
  } catch (_) {
    // ignore preload error
  }
}

export const useRenderMenuItem = (menuMode) =>
  // allRouters: AppRouteRecordRaw[] = [],
  {
    const renderMenuItem = (routers: AppRouteRecordRaw[], parentPath = '/') => {
      return routers
        .filter((v) => !v.meta?.hidden)
        .map((v) => {
          const meta = v.meta ?? {}
          const { oneShowingChild, onlyOneChild } = hasOneShowingChild(v.children, v)
          const fullPath = isUrl(v.path) ? v.path : pathResolve(parentPath, v.path) // getAllParentPath<AppRouteRecordRaw>(allRouters, v.path).join('/')

          if (
            oneShowingChild &&
            (!onlyOneChild?.children || onlyOneChild?.noShowingChildren) &&
            !meta?.alwaysShow
          ) {
            const itemIndex = onlyOneChild ? pathResolve(fullPath, onlyOneChild.path) : fullPath
            return (
              <div onMouseenter={() => prefetchRouteComponent(itemIndex)}>
                <ElMenuItem index={itemIndex}>
                  {{
                    default: () => renderMenuTitle(onlyOneChild ? onlyOneChild?.meta : meta)
                  }}
                </ElMenuItem>
              </div>
            )
          } else {
            return (
              <ElSubMenu
                index={fullPath}
                teleported
                popperClass={unref(menuMode) === 'vertical' ? `${prefixCls}-popper--vertical` : ''}
              >
                {{
                  title: () => renderMenuTitle(meta),
                  default: () => renderMenuItem(v.children!, fullPath)
                }}
              </ElSubMenu>
            )
          }
        })
    }

    return {
      renderMenuItem
    }
  }
