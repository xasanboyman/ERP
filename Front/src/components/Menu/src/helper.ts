import { ref, unref } from 'vue'
import { findPath } from '@/utils/tree'

type OnlyOneChildType = AppRouteRecordRaw & { noShowingChildren?: boolean }

interface HasOneShowingChild {
  oneShowingChild?: boolean
  onlyOneChild?: OnlyOneChildType
}

export const getAllParentPath = <T = Recordable>(treeData: T[], path: string) => {
  if (!treeData || !Array.isArray(treeData) || !path) return []
  const menuList = findPath(treeData, (n) => n && n.path === path) as AppRouteRecordRaw[]
  return (menuList || []).map((item) => item?.path).filter(Boolean) as string[]
}

export const hasOneShowingChild = (
  children: AppRouteRecordRaw[] = [],
  parent: AppRouteRecordRaw
): HasOneShowingChild => {
  const onlyOneChild = ref<OnlyOneChildType>()
  const safeChildren = Array.isArray(children) ? children : []

  const showingChildren = safeChildren.filter((v) => {
    if (!v) return false
    const meta = v.meta ?? {}
    if (meta.hidden) {
      return false
    } else {
      // Temp set(will be used if only has one showing child)
      onlyOneChild.value = v
      return true
    }
  })

  // When there is only one child router, the child router is displayed by default
  if (showingChildren.length === 1) {
    return {
      oneShowingChild: true,
      onlyOneChild: unref(onlyOneChild)
    }
  }

  // Show parent if there are no child router to display
  if (!showingChildren.length) {
    onlyOneChild.value = { ...(parent || {}), path: '', noShowingChildren: true } as any
    return {
      oneShowingChild: true,
      onlyOneChild: unref(onlyOneChild)
    }
  }

  return {
    oneShowingChild: false,
    onlyOneChild: unref(onlyOneChild)
  }
}
