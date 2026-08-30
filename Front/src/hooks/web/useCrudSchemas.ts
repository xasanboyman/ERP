import { reactive } from 'vue'
import { eachTree, treeMap, filter } from '@/utils/tree'
import { FormSchema } from '@/components/Form'
import { TableColumn } from '@/components/Table'
import { DescriptionsSchema } from '@/components/Descriptions'
import { useI18n } from '@/hooks/web/useI18n'

export type CrudSchema = Omit<TableColumn, 'children'> & {
  search?: CrudSearchParams
  table?: CrudTableParams
  form?: CrudFormParams
  detail?: CrudDescriptionsParams
  children?: CrudSchema[]
}

interface CrudSearchParams extends Omit<FormSchema, 'field'> {
  // 是否隐藏在查询项
  hidden?: boolean
}

interface CrudTableParams extends Omit<TableColumn, 'field'> {
  // 是否隐藏表头
  hidden?: boolean
}

interface CrudFormParams extends Omit<FormSchema, 'field'> {
  // 是否隐藏表单项
  hidden?: boolean
}

interface CrudDescriptionsParams extends Omit<DescriptionsSchema, 'field'> {
  // 是否隐藏表单项
  hidden?: boolean
}

interface AllSchemas {
  searchSchema: FormSchema[]
  tableColumns: TableColumn[]
  formSchema: FormSchema[]
  detailSchema: DescriptionsSchema[]
}

/**
 * @deprecated 不推荐使用，感觉过于繁琐，不是很灵活 可能会在某个版本中删除
 */
export const useCrudSchemas = (
  crudSchema: CrudSchema[]
): {
  allSchemas: AllSchemas
} => {
  // 所有结构数据
  const allSchemas = reactive<AllSchemas>({
    searchSchema: [],
    tableColumns: [],
    formSchema: [],
    detailSchema: []
  })

  const searchSchema = filterSearchSchema(crudSchema)
  // @ts-ignore
  allSchemas.searchSchema = searchSchema || []

  const tableColumns = filterTableSchema(crudSchema)
  allSchemas.tableColumns = tableColumns || []

  const formSchema = filterFormSchema(crudSchema)
  allSchemas.formSchema = formSchema

  const detailSchema = filterDescriptionsSchema(crudSchema)
  allSchemas.detailSchema = detailSchema

  return {
    allSchemas
  }
}

// 过滤 Search 结构
const filterSearchSchema = (crudSchema: CrudSchema[]): FormSchema[] => {
  const { t } = useI18n()
  const searchSchema: FormSchema[] = []
  const length = crudSchema.length

  for (let i = 0; i < length; i++) {
    const schemaItem = crudSchema[i]
    if (schemaItem.search?.hidden === true) {
      continue
    }
    const rawLabel = schemaItem.search?.label || schemaItem.label
    const searchSchemaItem = {
      component: schemaItem?.search?.component || 'Input',
      ...schemaItem.search,
      field: schemaItem.field,
      label: rawLabel ? t(rawLabel) : ''
    }

    searchSchema.push(searchSchemaItem)
  }

  return searchSchema
}

// 过滤 table 结构
const filterTableSchema = (crudSchema: CrudSchema[]): TableColumn[] => {
  const { t } = useI18n()
  const tableColumns = treeMap<CrudSchema>(crudSchema, {
    conversion: (schema: CrudSchema) => {
      if (!schema?.table?.hidden) {
        const rawLabel = schema.table?.label || schema.label
        return {
          ...schema,
          ...schema.table,
          label: rawLabel ? t(rawLabel) : ''
        }
      }
    }
  })

  // 第一次过滤会有 undefined 所以需要二次过滤
  return filter<TableColumn>(tableColumns as TableColumn[], (data) => {
    if (data.children === void 0) {
      delete data.children
    }
    return !!data.field
  })
}

// 过滤 form 结构
const filterFormSchema = (crudSchema: CrudSchema[]): FormSchema[] => {
  const { t } = useI18n()
  const formSchema: FormSchema[] = []
  const length = crudSchema.length

  for (let i = 0; i < length; i++) {
    const formItem = crudSchema[i]
    const rawLabel = formItem.form?.label || formItem.label
    const formSchemaItem = {
      component: formItem?.form?.component || 'Input',
      ...formItem.form,
      field: formItem.field,
      label: rawLabel ? t(rawLabel) : ''
    }

    formSchema.push(formSchemaItem)
  }

  return formSchema
}

// 过滤 descriptions 结构
const filterDescriptionsSchema = (crudSchema: CrudSchema[]): DescriptionsSchema[] => {
  const { t } = useI18n()
  const descriptionsSchema: FormSchema[] = []

  eachTree(crudSchema, (schemaItem: CrudSchema) => {
    // 判断是否隐藏
    if (!schemaItem?.detail?.hidden) {
      const rawLabel = schemaItem.detail?.label || schemaItem.label
      const descriptionsSchemaItem = {
        ...schemaItem.detail,
        field: schemaItem.field,
        label: rawLabel ? t(rawLabel) : ''
      }

      // 删除不必要的字段
      delete descriptionsSchemaItem.hidden

      descriptionsSchema.push(descriptionsSchemaItem)
    }
  })

  return descriptionsSchema
}
