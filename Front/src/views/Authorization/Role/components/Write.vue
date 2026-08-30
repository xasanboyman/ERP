<script setup lang="tsx">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { Form, FormSchema } from '@/components/Form'
import { useForm } from '@/hooks/web/useForm'
import { PropType, reactive, watch, ref, unref, nextTick } from 'vue'
import { useValidator } from '@/hooks/web/useValidator'
import {
  ElTree,
  ElCheckboxGroup,
  ElCheckbox,
  ElInput,
  ElButton,
  ElTag,
  ElTooltip
} from 'element-plus'
import { getMenuListApi } from '@/api/menu'
import { filter, eachTree } from '@/utils/tree'
import { Icon } from '@/components/Icon'

const { required } = useValidator()

const props = defineProps({
  currentRow: {
    type: Object as PropType<any>,
    default: () => null
  }
})

const treeRef = ref<any>()
const treeSearchKeyword = ref('')
const isExpandedAll = ref(true)

const filterNode = (value: string, data: any) => {
  if (!value) return true
  const title = data.title || data.meta?.title || ''
  return title.toLowerCase().includes(value.toLowerCase())
}

watch(treeSearchKeyword, (val) => {
  unref(treeRef)?.filter(val)
})

const toggleExpandAll = () => {
  isExpandedAll.value = !isExpandedAll.value
  const nodes = unref(treeRef)?.store?.nodesMap
  if (nodes) {
    for (const key in nodes) {
      nodes[key].expanded = isExpandedAll.value
    }
  }
}

// Auto-check a tree node AND its parent when it has permissions
const autoCheckNodeAndParent = (node: any) => {
  const tree = unref(treeRef)
  if (!tree) return

  const hasPerms = node.meta?.permission?.length > 0

  // Check this node
  tree.setChecked(node.id, hasPerms, false)

  // Find and check parent
  eachTree(treeData.value, (parent: any) => {
    if (parent.children && parent.children.some((c: any) => c.id === node.id)) {
      // If any child is checked, parent should be checked
      const anyChildChecked = parent.children.some((c: any) => {
        return c.meta?.permission?.length > 0 || tree.getCheckedKeys().includes(c.id)
      })
      if (anyChildChecked) {
        tree.setChecked(parent.id, true, false)
        // Also set parent view permissions if empty
        if (!parent.meta) parent.meta = { permission: [] }
        if (
          parent.permissionList &&
          Array.isArray(parent.permissionList) &&
          parent.meta.permission.length === 0
        ) {
          const viewPerms = parent.permissionList
            .filter((a: any) => a.value.includes('view'))
            .map((a: any) => a.value)
          parent.meta.permission =
            viewPerms.length > 0 ? viewPerms : parent.permissionList.map((a: any) => a.value)
        }
      }
    }
  })
}

// Called when action checkboxes change on the right panel
const onActionChange = (checkedActions: string[]) => {
  const node = unref(currentTreeData)
  if (!node) return
  autoCheckNodeAndParent(node)
}

const selectAllCurrentActions = () => {
  if (!unref(currentTreeData) || !unref(currentTreeData).permissionList) return
  if (!unref(currentTreeData).meta) {
    unref(currentTreeData).meta = { permission: [] }
  }
  const allValues = unref(currentTreeData).permissionList.map((v: any) => v.value)
  unref(currentTreeData).meta.permission = allValues
  autoCheckNodeAndParent(unref(currentTreeData))
}

const clearAllCurrentActions = () => {
  if (!unref(currentTreeData) || !unref(currentTreeData).meta) return
  unref(currentTreeData).meta.permission = []
  const tree = unref(treeRef)
  if (tree) {
    const node = unref(currentTreeData)
    tree.setChecked(node.id, false, false)
    // If no siblings are checked, uncheck parent too
    eachTree(treeData.value, (parent: any) => {
      if (parent.children && parent.children.some((c: any) => c.id === node.id)) {
        const anyChildChecked = parent.children.some((c: any) => {
          return c.meta?.permission?.length > 0
        })
        if (!anyChildChecked) {
          tree.setChecked(parent.id, false, false)
          if (parent.meta) parent.meta.permission = []
        }
      }
    })
  }
}

const onCheck = (node: any, state: any) => {
  const checkedKeys = state.checkedKeys || []
  const isChecked = checkedKeys.includes(node.id)

  if (!node.meta) node.meta = { permission: [] }

  if (isChecked) {
    // When tree checkbox is checked, enable all actions for this node
    if (node.permissionList && Array.isArray(node.permissionList)) {
      node.meta.permission = node.permissionList.map((a: any) => a.value)
    }
    // Auto-enable parent permissions
    eachTree(treeData.value, (parent: any) => {
      if (parent.children && parent.children.some((c: any) => c.id === node.id)) {
        if (!parent.meta) parent.meta = { permission: [] }
        if (
          parent.permissionList &&
          Array.isArray(parent.permissionList) &&
          parent.meta.permission.length === 0
        ) {
          const viewPerms = parent.permissionList
            .filter((a: any) => a.value.includes('view'))
            .map((a: any) => a.value)
          parent.meta.permission =
            viewPerms.length > 0 ? viewPerms : parent.permissionList.map((a: any) => a.value)
        }
      }
    })
  } else {
    node.meta.permission = []
    // Also clear all children permissions when parent is unchecked
    if (node.children && Array.isArray(node.children)) {
      eachTree([node], (child: any) => {
        if (child.meta) child.meta.permission = []
      })
    }
  }
}

const formSchema = ref<Array<FormSchema>>([
  {
    field: 'roleName',
    label: 'Rol Nomi',
    component: 'Input',
    colProps: {
      span: 9
    },
    componentProps: {
      placeholder: 'Masalan: Senior Kassir, Omborchi'
    }
  },
  {
    field: 'status',
    label: 'Holati',
    component: 'Select',
    colProps: {
      span: 6
    },
    componentProps: {
      options: [
        {
          label: "O'chirilgan",
          value: 0
        },
        {
          label: 'Faol',
          value: 1
        }
      ]
    }
  },
  {
    field: 'remark',
    label: 'Izoh',
    component: 'Input',
    colProps: {
      span: 9
    },
    componentProps: {
      placeholder: 'Rol va ruxsatlar haqida izoh...'
    }
  },
  {
    field: 'menu',
    label: 'Ruxsatlar',
    colProps: {
      span: 24
    },
    formItemProps: {
      slots: {
        default: () => {
          return (
            <div class="role-permission-matrix w-full border border-[var(--el-border-color-lighter)] rounded-2xl p-16px bg-[var(--el-fill-color-light)] dark:bg-slate-950/95 dark:border-slate-800 flex flex-col flex-1 min-h-0 shadow-sm">
              {/* Matrix Content */}
              <div class="flex gap-20px flex-1 min-h-0">
                {/* Left Tree Column */}
                <div class="w-1/2 border-r border-[var(--el-border-color-lighter)] dark:border-slate-800/90 pr-16px flex flex-col h-full min-h-0">
                  <div class="flex items-center justify-between mb-10px pb-8px border-b border-[var(--el-border-color-lighter)] dark:border-slate-800/80 flex-shrink-0">
                    <div class="flex items-center gap-8px text-14px font-bold text-blue-600 dark:text-blue-400">
                      <Icon
                        icon="vi-ep:folder-opened"
                        size={18}
                        class="text-blue-600 dark:text-blue-400"
                      />
                      <span>1. Sahifalar & Menyular</span>
                    </div>
                    <ElButton
                      size="small"
                      type="info"
                      link
                      onClick={toggleExpandAll}
                      class="!text-12px !text-slate-500 dark:!text-slate-400 hover:!text-blue-600"
                    >
                      {isExpandedAll.value ? "Yig'ish" : 'Yoyish'}
                    </ElButton>
                  </div>

                  {/* Filter Search */}
                  <div class="mb-10px flex-shrink-0">
                    <ElInput
                      v-model={treeSearchKeyword.value}
                      placeholder="Menyu bo'yicha qidirish..."
                      clearable
                      prefix-icon="vi-ep:search"
                      class="custom-tree-search"
                    />
                  </div>

                  {/* Tree */}
                  <div class="flex-1 overflow-y-auto pr-4px min-h-0 custom-role-tree">
                    <ElTree
                      ref={treeRef}
                      show-checkbox
                      node-key="id"
                      highlight-current
                      check-strictly={false}
                      default-expand-all
                      expand-on-click-node={false}
                      filter-node-method={filterNode}
                      data={treeData.value}
                      onNode-click={nodeClick}
                      onCheck={onCheck}
                    >
                      {{
                        default: (data: any) => {
                          const iconName =
                            data.data.icon || data.data.meta?.icon || 'vi-ep:document'
                          const isSelected = unref(currentTreeData)?.id === data.data.id
                          const permCount = data.data.meta?.permission?.length || 0
                          const totalPerms = data.data.permissionList?.length || 0

                          return (
                            <div
                              class={`flex items-center justify-between w-full py-6px px-8px rounded-lg transition-all ${isSelected ? 'text-blue-700 dark:text-blue-300 bg-blue-500/10 dark:bg-blue-500/20 font-bold' : 'text-slate-800 dark:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800/60 font-medium'}`}
                            >
                              <div class="flex items-center gap-8px min-w-0 flex-1 overflow-hidden">
                                <Icon
                                  icon={iconName}
                                  size={16}
                                  class={`flex-shrink-0 ${isSelected ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-400'}`}
                                />
                                <span
                                  class={`truncate text-13px ${isSelected ? 'text-blue-700 dark:text-blue-300 font-bold' : 'text-slate-800 dark:text-slate-200'}`}
                                >
                                  {data.data.title || data.data.meta?.title || 'Menyu'}
                                </span>
                              </div>
                              {totalPerms > 0 && (
                                <span
                                  class={`ml-6px text-11px px-6px py-1px rounded-full font-bold flex-shrink-0 ${permCount > 0 ? 'bg-emerald-100 text-emerald-700 border border-emerald-300 dark:bg-emerald-500/20 dark:text-emerald-300 dark:border-emerald-500/40' : 'bg-slate-200 text-slate-600 border border-slate-300 dark:bg-slate-800/80 dark:text-slate-500 dark:border-slate-700/60'}`}
                                >
                                  {permCount}/{totalPerms}
                                </span>
                              )}
                            </div>
                          )
                        }
                      }}
                    </ElTree>
                  </div>
                </div>

                {/* Right Action Permissions Column */}
                <div class="w-1/2 pl-4px flex flex-col h-full min-h-0">
                  <div class="flex items-center justify-between mb-10px pb-8px border-b border-[var(--el-border-color-lighter)] dark:border-slate-800/80 flex-shrink-0">
                    <div class="flex items-center gap-8px text-14px font-bold text-emerald-600 dark:text-emerald-400 min-w-0 overflow-hidden">
                      <Icon
                        icon="vi-ep:operation"
                        size={18}
                        class="text-emerald-600 dark:text-emerald-400 flex-shrink-0"
                      />
                      <span class="truncate">
                        2. Amallar: {currentTreeData.value?.title || 'Menyu tanlang'}
                      </span>
                    </div>

                    {unref(currentTreeData) &&
                      unref(currentTreeData)?.permissionList &&
                      unref(currentTreeData).permissionList.length > 0 && (
                        <div class="flex items-center gap-6px flex-shrink-0 ml-8px">
                          <ElButton
                            type="primary"
                            link
                            onClick={selectAllCurrentActions}
                            class="!text-12px !font-bold text-blue-600 dark:text-blue-400"
                          >
                            {t('erp.selectAll')}
                          </ElButton>
                          <span class="text-slate-400 dark:text-slate-600">|</span>
                          <ElButton
                            type="info"
                            link
                            onClick={clearAllCurrentActions}
                            class="!text-12px !text-slate-500 dark:!text-slate-400 !font-semibold"
                          >
                            {t('common.reset')}
                          </ElButton>
                        </div>
                      )}
                  </div>

                  <div class="flex-1 overflow-y-auto min-h-0 pr-4px">
                    {unref(currentTreeData) &&
                    unref(currentTreeData)?.permissionList &&
                    unref(currentTreeData).permissionList.length > 0 ? (
                      <ElCheckboxGroup
                        v-model={unref(currentTreeData).meta.permission}
                        onChange={onActionChange}
                        class="flex flex-col gap-12px mt-6px"
                      >
                        {unref(currentTreeData)?.permissionList.map((v: any) => {
                          const isChecked = unref(currentTreeData).meta?.permission?.includes(
                            v.value
                          )
                          return (
                            <ElCheckbox
                              value={v.value}
                              key={v.value}
                              class={`!mr-0 !py-10px !px-14px border rounded-xl transition-all flex items-center ${isChecked ? 'bg-emerald-50 border-emerald-400 text-emerald-900 shadow-xs dark:bg-emerald-950/50 dark:border-emerald-500/60 dark:text-emerald-200' : 'bg-white border-slate-200 text-slate-800 hover:border-slate-300 dark:bg-slate-900/90 dark:border-slate-800 dark:text-slate-200 dark:hover:border-slate-700'}`}
                            >
                              <div class="flex items-center gap-10px">
                                <div
                                  class={`w-26px h-26px rounded-lg flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}`}
                                >
                                  <Icon icon={v.icon || 'vi-ep:check'} size={15} />
                                </div>
                                <span
                                  class={`text-13px ${isChecked ? 'text-emerald-900 dark:text-emerald-200 font-bold' : 'text-slate-800 dark:text-slate-200 font-semibold'}`}
                                >
                                  {v.label}
                                </span>
                              </div>
                            </ElCheckbox>
                          )
                        })}
                      </ElCheckboxGroup>
                    ) : (
                      <div class="text-13px text-slate-500 dark:text-slate-400 italic mt-20px p-20px border border-slate-200 dark:border-slate-800 rounded-2xl bg-white dark:bg-slate-900/60 flex flex-col items-center justify-center gap-10px text-center">
                        <div class="w-44px h-44px rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                          <Icon
                            icon="vi-ep:info-filled"
                            size={22}
                            class="text-blue-500 dark:text-blue-400"
                          />
                        </div>
                        <span class="max-w-280px leading-relaxed">
                          Chap tomondan xohlagan menyungizni tanlang va shu menyu uchun xususiy
                          amallarni belgiling.
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        }
      }
    }
  }
])

const currentTreeData = ref()
const nodeClick = (treeData: any) => {
  if (!treeData.meta) {
    treeData.meta = { permission: [] }
  } else if (!treeData.meta.permission) {
    treeData.meta.permission = []
  }
  currentTreeData.value = treeData
}

const rules = reactive({
  roleName: [required()],
  status: [required()]
})

const { formRegister, formMethods } = useForm()
const { setValues, getFormData, getElFormExpose } = formMethods

const treeData = ref([])

const syncCurrentRowPermissions = async () => {
  if (!props.currentRow || !treeData.value || treeData.value.length === 0) return
  await nextTick()

  const activePermissions = new Set<string>()
  let isSuperAdmin = false

  if (Array.isArray(props.currentRow.permissions)) {
    props.currentRow.permissions.forEach((p: any) => {
      if (typeof p === 'string') {
        activePermissions.add(p)
        if (p === '*.*.*' || p === '*') isSuperAdmin = true
      } else if (p && typeof p === 'object') {
        if (p.path) activePermissions.add(p.path)
        if (p.meta && Array.isArray(p.meta.permission)) {
          p.meta.permission.forEach((perm: string) => activePermissions.add(perm))
        }
      }
    })
  }

  if (Array.isArray(props.currentRow.menu)) {
    eachTree(props.currentRow.menu, (item: any) => {
      if (item.path) activePermissions.add(item.path)
      if (item.id) activePermissions.add(String(item.id))
      if (item.meta && Array.isArray(item.meta.permission)) {
        item.meta.permission.forEach((p: string) => activePermissions.add(p))
      }
    })
  }

  const checkedNodeIds: (string | number)[] = []

  eachTree(treeData.value, (node: any) => {
    if (!node.meta) node.meta = { permission: [] }

    const fullPath = (node.path?.startsWith('/') ? node.path : `/${node.path}`).toLowerCase()
    const isPathChecked =
      isSuperAdmin ||
      activePermissions.has('*.*.*') ||
      activePermissions.has(node.path) ||
      activePermissions.has(fullPath) ||
      activePermissions.has(String(node.id)) ||
      activePermissions.has(node.name)

    const nodeActions: string[] = []
    if (node.permissionList && Array.isArray(node.permissionList)) {
      node.permissionList.forEach((action: any) => {
        if (isSuperAdmin || activePermissions.has('*.*.*') || activePermissions.has(action.value)) {
          nodeActions.push(action.value)
        }
      })

      if (isPathChecked && nodeActions.length === 0) {
        node.permissionList.forEach((action: any) => {
          nodeActions.push(action.value)
        })
      }
    }

    node.meta.permission = nodeActions

    if (isPathChecked || nodeActions.length > 0) {
      checkedNodeIds.push(node.id)
    }
  })

  if (unref(treeRef)) {
    unref(treeRef).setCheckedKeys([])
    for (const id of checkedNodeIds) {
      unref(treeRef).setChecked(id, true, false)
    }
  }

  if (checkedNodeIds.length > 0) {
    const firstChecked = treeData.value.find((n: any) => checkedNodeIds.includes(n.id))
    if (firstChecked) {
      currentTreeData.value = firstChecked
    }
  }
}

const getMenuList = async () => {
  const res = await getMenuListApi()
  if (res && res.data) {
    treeData.value = res.data.list || []
    if (treeData.value.length > 0) {
      currentTreeData.value = treeData.value[0]
    }
    await syncCurrentRowPermissions()
  }
}

getMenuList()

const submit = async () => {
  const elForm = await getElFormExpose()
  const valid = await elForm?.validate().catch((err) => {
    console.log(err)
  })
  if (valid) {
    const formData = await getFormData()
    const checkedKeys = unref(treeRef)?.getCheckedKeys() || []
    const halfCheckedKeys = unref(treeRef)?.getHalfCheckedKeys() || []
    const allSelectedKeys = Array.from(new Set([...checkedKeys, ...halfCheckedKeys]))

    const data = filter(unref(treeData), (item: any) => {
      return allSelectedKeys.includes(item.id)
    })
    formData.menu = data || []

    const permissions: string[] = []
    eachTree(unref(treeData), (item: any) => {
      if (allSelectedKeys.includes(item.id)) {
        if (item.path) {
          permissions.push(item.path)
          const fullPath = item.path.startsWith('/') ? item.path : `/${item.path}`
          permissions.push(fullPath)

          // Find parent path if child
          let parent: any = null
          eachTree(unref(treeData), (p: any) => {
            if (p.children && p.children.some((c: any) => c.id === item.id)) {
              parent = p
            }
          })
          if (parent && parent.path) {
            const parentClean = parent.path.startsWith('/') ? parent.path : `/${parent.path}`
            permissions.push(parentClean)
            const combined = `${parentClean}/${item.path}`.replace(/\/+/g, '/')
            permissions.push(combined)
          }
        }
        if (item.meta && item.meta.permission && Array.isArray(item.meta.permission)) {
          permissions.push(...item.meta.permission)
        }
      }
    })

    formData.permissions = Array.from(new Set(permissions))
    return formData
  }
}

watch(
  () => props.currentRow,
  async (currentRow) => {
    if (!currentRow) return
    setValues(currentRow)
    await syncCurrentRowPermissions()
  },
  {
    deep: true,
    immediate: true
  }
)

defineExpose({
  submit
})
</script>

<template>
  <Form
    :rules="rules"
    @register="formRegister"
    :schema="formSchema"
    label-position="top"
    class="role-write-form h-full flex flex-col flex-1 min-h-0"
  />
</template>

<style lang="less">
/* Hide scrollbars visually while keeping scrollability */
.custom-role-tree,
.role-permission-matrix * {
  scrollbar-width: none !important;
  -ms-overflow-style: none !important;

  &::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
  }
}

/* Override ElTree's built-in node highlight/hover backgrounds to prevent double-blue overlay */
.custom-role-tree {
  .el-tree-node__content {
    background-color: transparent !important;
    padding: 0 !important;
    height: auto !important;
    min-height: 36px;

    &:hover {
      background-color: transparent !important;
    }
  }

  /* Remove ElTree's is-current highlight */
  .el-tree-node.is-current > .el-tree-node__content {
    background-color: transparent !important;
  }

  /* Remove ElTree's is-focusable focus state */
  .el-tree-node:focus > .el-tree-node__content {
    background-color: transparent !important;
  }

  /* Make tree node expand icon align nicely */
  .el-tree-node__expand-icon {
    color: #64748b;
    font-size: 14px;
    padding: 4px;
  }

  /* Tree checkbox styling */
  .el-checkbox {
    margin-right: 4px;
  }
}
</style>
