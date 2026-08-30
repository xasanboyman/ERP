import { getWorkerListApi, saveWorkerApi, deleteWorkerApi } from '@/api/worker'
import {
  getProductListApi,
  saveProductApi,
  deleteProductApi,
  searchClassifierApi
} from '@/api/product'
import { getDepartmentApi, saveDepartmentApi, deleteDepartmentApi } from '@/api/department'
import { getSalesListApi, getDebtorsApi, repayDebtApi, getSaleReceiptApi } from '@/api/sales'
import { getPendingSalesPushApi, respondSalesPushApi } from '@/api/device'
import {
  getOrderListApi,
  saveOrderApi,
  deleteOrderApi,
  startProductionApi,
  getTaskListApi,
  updateTaskStatusApi
} from '@/api/cutting'
import { getQrListApi, saveQrApi, deleteQrApi } from '@/api/qr'
import { getSalaryListApi, saveSalaryApi, bulkSalaryPayoutApi } from '@/api/salary'
import { getRoleListApi, saveRoleApi, deleteRoleApi } from '@/api/role'
import { getBranchListApi, saveBranchApi } from '@/api/branch'
import request from '@/axios'
import { useEventBus } from '@/hooks/event/useEventBus'

export const notifyDataUpdated = (action: string, params?: any) => {
  try {
    const bus = useEventBus()
    bus.emit('ai-data-updated', { action, params })
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('ai-data-updated', { detail: { action, params } }))
    }

    if (
      ['create_product', 'add_product_stock', 'update_product', 'delete_product'].includes(action)
    ) {
      bus.emit('refresh-products')
    }
    if (['create_worker', 'update_worker', 'delete_worker'].includes(action)) {
      bus.emit('refresh-workers')
    }
    if (['create_department', 'delete_department'].includes(action)) {
      bus.emit('refresh-departments')
    }
    if (['create_position'].includes(action)) {
      bus.emit('refresh-positions')
    }
    if (['repay_debt'].includes(action)) {
      bus.emit('refresh-debtors')
      bus.emit('refresh-sales')
    }
    if (['create_salary', 'salary_payout'].includes(action)) {
      bus.emit('refresh-salaries')
    }
    if (['create_branch'].includes(action)) {
      bus.emit('refresh-branches')
    }
    if (
      [
        'create_cutting_order',
        'delete_cutting_order',
        'start_production',
        'update_task_status'
      ].includes(action)
    ) {
      bus.emit('refresh-cutting')
    }
    if (['create_timesheet', 'create_staff_output', 'create_staff_adjustment'].includes(action)) {
      bus.emit('refresh-hr')
    }
    if (['create_role', 'delete_role'].includes(action)) {
      bus.emit('refresh-roles')
    }
  } catch (e) {
    console.warn('[AI Dispatcher] Event emit warning:', e)
  }
}
import {
  getPositionListApi,
  savePositionApi,
  getAdjustmentListApi,
  saveAdjustmentApi,
  saveTimesheetApi,
  getOutputListApi,
  saveOutputApi
} from '@/api/staff_hr'

export interface AIDispatchResult {
  code: number
  message: string
  data?: any
  requests: string[]
}

const extractBrandFromQuery = (rawQuery: string, classifierBrand?: string): string => {
  if (classifierBrand && classifierBrand.trim() && classifierBrand.trim() !== '—') {
    return classifierBrand.trim().toUpperCase()
  }
  const firstWord = rawQuery.trim().split(/\s+/)[0] || ''
  if (firstWord.length >= 2) return firstWord.toUpperCase()
  return 'GENERIC'
}

const handleProductCreationOrUpdate = async (params: any, isAddStock = false) => {
  const query = params.name || params.query || params.product_name || 'Yangi Mahsulot'
  const addedQty = Number(params.added_quantity || params.quantity || (isAddStock ? 1 : 0))

  const priceVal = params.price !== undefined ? Number(params.price) : undefined
  const costVal = params.cost !== undefined ? Number(params.cost) : undefined
  const expDateVal = params.expiration_date || params.expiry_date || undefined
  const brandVal = params.brand_name || params.brand || undefined

  const searchUrl = `/product/list?productName=${encodeURIComponent(query)}`
  const requestsList: string[] = [`GET ${searchUrl}`]

  // 1. Check local stock database by name
  const searchRes = await getProductListApi({ productName: query })
  let list = (searchRes.data as any)?.list || searchRes.data || []

  if (!list.length) {
    requestsList.push('GET /product/list [Full Catalog Token Search]')
    const allRes = await getProductListApi({})
    const allList = (allRes.data as any)?.list || allRes.data || []
    const terms = query
      .toLowerCase()
      .split(/\s+/)
      .filter((t: string) => t.length > 0)
    list = allList.filter((p: any) => {
      const pName = (p.productName || p.name || '').toLowerCase()
      const pBrand = (p.brand_name || '').toLowerCase()
      const pAttr = (p.attribute_name || '').toLowerCase()
      const fullText = `${pName} ${pBrand} ${pAttr}`
      return terms.some((t: string) => t.length > 1 && fullText.includes(t))
    })
  }

  // 2. Existing Product Match in Stock → update quantity/price
  if (list.length > 0) {
    const match = list[0]
    const currentQty = Number(match.quantityInStock || match.quantity || 0)
    const newQty = isAddStock ? currentQty + (addedQty || 1) : addedQty || currentQty
    const finalPrice = priceVal !== undefined ? priceVal : match.price || 0
    const finalCost = costVal !== undefined ? costVal : match.cost || 0
    const finalExpDate = expDateVal || match.expiration_date || undefined
    const finalBrand = brandVal || match.brand_name || extractBrandFromQuery(query)

    const updatePayload: any = {
      id: String(match.id),
      productName: match.productName || match.name,
      SKU: match.SKU,
      category: match.category,
      price: finalPrice,
      cost: finalCost,
      quantityInStock: newQty,
      brand_name: finalBrand,
      expiration_date: finalExpDate
    }

    requestsList.push(
      `POST /product/save [ID: ${match.id}, Stock: ${newQty}, Price: $${finalPrice}]`
    )
    await saveProductApi(updatePayload)

    let pricePrompt = ''
    if (!finalPrice || finalPrice === 0) {
      pricePrompt = `\n\n⚠️ DIQQAT: Mahsulot sotuv narxi ($0) yoki tannarxi ($0) ko'rsatilmadi! Iltimos, sotuv narxi, tannarxi va yaroqlilik muddatini (YYYY-MM-DD) kiriting!`
    }

    return {
      code: 0,
      message: `Mahsulot '${match.productName}' [Brend: ${finalBrand}] omborda topildi va yangilandi! +${addedQty || 1} dona qo'shildi (Eski: ${currentQty}, Yangi: ${newQty} ta). Sotuv narxi: $${finalPrice}, Tannarxi: $${finalCost}.${pricePrompt}`,
      data: {
        id: match.id,
        productName: match.productName,
        brand_name: finalBrand,
        price: finalPrice,
        cost: finalCost,
        previousQuantity: currentQty,
        addedQuantity: addedQty || 1,
        newQuantity: newQty,
        expiration_date: finalExpDate
      },
      requests: requestsList
    }
  }

  // 3. Search 411,000+ item State Classifier (/classifier/list)
  let cList: any[] = []
  requestsList.push(`GET /classifier/list?search=${encodeURIComponent(query)}&page=1&page_size=20`)
  try {
    const classRes = await searchClassifierApi({ search: query, page: 1, page_size: 20 })
    cList = classRes?.data || []
  } catch (_) {
    // ignore classifier search failure
  }

  // 4. Brand keyword fallback (e.g. "Pepsi can" → search "Pepsi")
  const brandSearchTerm = query.trim().split(/\s+/)[0] || query
  if (!cList.length && brandSearchTerm.length >= 2) {
    requestsList.push(
      `GET /classifier/list?search=${encodeURIComponent(brandSearchTerm)} [Brand Fallback]`
    )
    try {
      const brandRes = await searchClassifierApi({
        search: brandSearchTerm,
        page: 1,
        page_size: 20
      })
      const bItems = brandRes?.data || []
      cList = bItems
    } catch (_) {
      // ignore brand search failure
    }
  }

  // 5. Create new product (with classifier data if found)
  let cItem: any = null
  let productNameToUse = query
  let finalBrand = brandVal || extractBrandFromQuery(query)
  let classifierId = undefined
  let shtrixCode = ''
  let mxikCode = ''
  let unitToUse = 'dona'
  let categoryToUse = ''

  if (cList.length > 0) {
    cItem = cList[0]
    classifierId = cItem.id
    shtrixCode = cItem.shtrix_code || ''
    mxikCode = cItem.mxik_code || ''
    unitToUse = cItem.unit || 'dona'
    if (cItem.brand_name) finalBrand = cItem.brand_name.toUpperCase()
    categoryToUse = cItem.group_name || cItem.class_name || ''

    if (cItem.mxik_name && cItem.mxik_name.length < 80) {
      productNameToUse = cItem.mxik_name
    } else {
      productNameToUse = query
    }
  }

  const sku = shtrixCode
    ? `SKU-${shtrixCode}`
    : mxikCode
      ? `SKU-${mxikCode}`
      : `SKU-${Math.floor(Math.random() * 899999 + 100000)}`
  const finalPrice = priceVal !== undefined ? priceVal : 0
  const finalCost = costVal !== undefined ? costVal : 0

  const newProductPayload: any = {
    productName: productNameToUse.trim(),
    SKU: sku,
    category: categoryToUse,
    price: finalPrice,
    cost: finalCost,
    quantityInStock: addedQty || 1,
    classifier_id: classifierId,
    shtrix_code: shtrixCode,
    mxik_code: mxikCode,
    brand_name: finalBrand,
    attribute_name: cItem?.attribute_name || '',
    unit: unitToUse,
    expiration_date: expDateVal || undefined,
    remark: cItem
      ? 'Milliy Mahsulotlar Bazasidan topilib AI orqali yaratildi'
      : 'AI yordamchisi orqali omborga kiritildi'
  }

  requestsList.push(`POST /product/save [New: ${productNameToUse}, Brand: ${finalBrand}]`)
  const createRes = await saveProductApi(newProductPayload)

  const classifierNotice = cItem
    ? ` (Milliy Mahsulotlar Bazasidan '[${finalBrand}] ${cItem.mxik_name || brandSearchTerm}' topildi va bog'landi)`
    : ` (Bazada topilmadi, yangi [${finalBrand}] nomi bilan yaratildi)`

  let priceNotice = ''
  if (!finalPrice || finalPrice === 0) {
    priceNotice = `\n\n⚠️ Sotuv narxi va tannarx kiritilmadi ($0). Iltimos, sotuv narxi, tannarxi va yaroqlilik muddatini (YYYY-MM-DD) ayting!`
  }

  return {
    code: 0,
    message: `Mahsulot '${productNameToUse}' [Brend: ${finalBrand}] omborga +${addedQty || 1} dona bilan yaratildi!${classifierNotice}.${priceNotice}`,
    data: createRes.data,
    requests: requestsList
  }
}

import { useUserStore } from '@/store/modules/user'

const PERMISSION_MAP: Record<string, { resource: string; action: string; legacy?: string[] }> = {
  create_worker: {
    resource: 'hr.sotrudniki',
    action: 'create',
    legacy: ['worker:create', 'hr:create']
  },
  update_worker: {
    resource: 'hr.sotrudniki',
    action: 'update',
    legacy: ['worker:edit', 'hr:edit']
  },
  delete_worker: {
    resource: 'hr.sotrudniki',
    action: 'delete',
    legacy: ['worker:delete', 'hr:delete']
  },
  list_workers: { resource: 'hr.sotrudniki', action: 'view', legacy: ['worker:view', 'hr:view'] },

  create_product: {
    resource: 'products.spisok_tovarov',
    action: 'create',
    legacy: ['product:create', 'products:create']
  },
  add_product_stock: {
    resource: 'products.spisok_tovarov',
    action: 'create',
    legacy: ['product:create', 'product:edit', 'pos:sell']
  },
  update_product: {
    resource: 'products.spisok_tovarov',
    action: 'update',
    legacy: ['product:edit', 'products:edit']
  },
  delete_product: {
    resource: 'products.spisok_tovarov',
    action: 'delete',
    legacy: ['product:delete', 'products:delete']
  },
  list_products: {
    resource: 'products.spisok_tovarov',
    action: 'view',
    legacy: ['product:view', 'products:view', 'pos:sell', 'pos:history']
  },
  search_product: {
    resource: 'products.spisok_tovarov',
    action: 'view',
    legacy: ['product:view', 'products:view', 'pos:sell', 'pos:history']
  },

  create_department: {
    resource: 'hr.otdel',
    action: 'create',
    legacy: ['department:create', 'hr:create']
  },
  list_departments: {
    resource: 'hr.otdel',
    action: 'view',
    legacy: ['department:view', 'hr:view']
  },

  create_position: {
    resource: 'hr.dolzhnosti',
    action: 'create',
    legacy: ['position:create', 'hr:create']
  },
  list_positions: {
    resource: 'hr.dolzhnosti',
    action: 'view',
    legacy: ['position:view', 'hr:view']
  },

  create_timesheet: {
    resource: 'hr.tabel',
    action: 'create',
    legacy: ['timesheet:create', 'timesheet:view', 'hr:view']
  },

  create_staff_output: {
    resource: 'hr.vyrabotka',
    action: 'create',
    legacy: ['output:create', 'hr:create']
  },
  list_staff_outputs: {
    resource: 'hr.vyrabotka',
    action: 'view',
    legacy: ['output:view', 'hr:view']
  },

  create_staff_adjustment: {
    resource: 'hr.korrektirovki',
    action: 'create',
    legacy: ['adjustment:create', 'hr:create']
  },
  list_staff_adjustments: {
    resource: 'hr.korrektirovki',
    action: 'view',
    legacy: ['adjustment:view', 'hr:view']
  },

  list_users: { resource: 'staff.users', action: 'view', legacy: ['user:view', 'staff:view'] },

  list_sales: {
    resource: 'sales.istoriya_prodazh',
    action: 'view',
    legacy: ['pos:history', 'sales:view', 'pos:sell']
  },
  get_sale_receipt: {
    resource: 'sales.istoriya_prodazh',
    action: 'view',
    legacy: ['pos:history', 'sales:view', 'pos:sell']
  },
  list_debtors: {
    resource: 'sales.istoriya_prodazh',
    action: 'view',
    legacy: ['pos:nasiya', 'pos:history', 'sales:view', 'debtors:view']
  },
  repay_debt: {
    resource: 'sales.istoriya_prodazh',
    action: 'create',
    legacy: ['pos:nasiya', 'pos:sell', 'sales:create', 'debtors:repay']
  },

  list_salaries: {
    resource: 'hr.vedomost',
    action: 'view',
    legacy: ['salary:view', 'payroll:view']
  },
  create_salary: {
    resource: 'hr.vedomost',
    action: 'create',
    legacy: ['salary:create', 'payroll:create']
  },
  salary_payout: {
    resource: 'hr.vedomost',
    action: 'create',
    legacy: ['salary:payout', 'payroll:payout']
  },

  list_roles: { resource: 'staff.roles', action: 'view', legacy: ['role:view', 'staff:view'] },
  create_role: {
    resource: 'staff.roles',
    action: 'create',
    legacy: ['role:create', 'staff:create']
  },
  delete_role: {
    resource: 'staff.roles',
    action: 'delete',
    legacy: ['role:delete', 'staff:delete']
  },

  list_branches: {
    resource: 'products.spisok_tovarov',
    action: 'view',
    legacy: ['branch:view', 'branch:list']
  },
  create_branch: {
    resource: 'products.spisok_tovarov',
    action: 'create',
    legacy: ['branch:create']
  },

  create_cutting_order: {
    resource: 'cutting.raskroi',
    action: 'create',
    legacy: ['cutting:create']
  },
  delete_cutting_order: {
    resource: 'cutting.raskroi',
    action: 'delete',
    legacy: ['cutting:delete']
  },
  list_cutting_orders: { resource: 'cutting.raskroi', action: 'view', legacy: ['cutting:view'] },
  start_production: { resource: 'cutting.raskroi', action: 'update', legacy: ['cutting:edit'] },
  list_cutting_tasks: { resource: 'cutting.raskroi', action: 'view', legacy: ['cutting:view'] },
  update_task_status: { resource: 'cutting.raskroi', action: 'update', legacy: ['cutting:edit'] },

  generate_qr_code: { resource: 'qr_codes.print', action: 'create', legacy: ['qr:create'] },
  list_qr_codes: { resource: 'qr_codes.print', action: 'view', legacy: ['qr:view'] },
  delete_qr_code: { resource: 'qr_codes.print', action: 'delete', legacy: ['qr:delete'] }
}

async function _dispatchAIFunctionInternal(action: string, params: any): Promise<AIDispatchResult> {
  console.log(`[AI Dispatcher] Executing action: ${action}`, params)

  try {
    const userStore = useUserStore()
    const userInfo = userStore.getUserInfo
    const isSuper =
      userInfo?.role === 'admin' ||
      String(userInfo?.roleId) === '1' ||
      userInfo?.permissions?.includes('*.*.*')

    if (!isSuper) {
      const req = PERMISSION_MAP[action]
      if (req) {
        const userPerms = userInfo?.permissions || []
        const permStr = `${req.resource}:${req.action}`
        const permStar = `${req.resource}:*`
        const hasPerm =
          userPerms.includes(permStr) ||
          userPerms.includes(permStar) ||
          userPerms.includes('*.*.*') ||
          (req.legacy && req.legacy.some((l: string) => userPerms.includes(l)))

        if (!hasPerm) {
          return {
            code: 403,
            message: `Xavfsizlik cheklovi: '${action}' amali uchun ruxsatingiz yo'q.`,
            requests: []
          }
        }
      }
    }
    switch (action) {
      // ═══════════════════════════════════════════════════════
      // WORKERS  →  /worker/*
      // ═══════════════════════════════════════════════════════
      case 'create_worker': {
        const firstName = params.first_name || params.name || ''
        const lastName = params.last_name || ''
        const fullName = [firstName, lastName].filter(Boolean).join(' ') || 'Xodim'
        const payload: any = {
          name: fullName,
          phone: params.phone || '',
          role: params.position || params.department || params.role || 'Xodim',
          baseSalary: params.salary
            ? Number(params.salary)
            : params.baseSalary
              ? Number(params.baseSalary)
              : 0,
          status: 1
        }
        const res = await saveWorkerApi(payload)
        return {
          code: 0,
          message: `Xodim '${fullName}' muvaffaqiyatli yaratildi.`,
          data: res.data,
          requests: [`POST /worker/save [Name: ${fullName}, Phone: ${payload.phone}]`]
        }
      }

      case 'update_worker': {
        if (!params.worker_id)
          return { code: 500, message: "worker_id ko'rsatilmadi.", requests: [] }
        const payload: any = { id: String(params.worker_id) }
        if (params.first_name || params.last_name) {
          payload.name = [params.first_name, params.last_name].filter(Boolean).join(' ')
        }
        if (params.name) payload.name = params.name
        if (params.position) payload.role = params.position
        if (params.role) payload.role = params.role
        if (params.phone) payload.phone = params.phone
        if (params.salary) payload.baseSalary = Number(params.salary)
        const res = await saveWorkerApi(payload)
        return {
          code: 0,
          message: `Xodim muvaffaqiyatli yangilandi.`,
          data: res.data,
          requests: [`POST /worker/save [ID: ${params.worker_id}]`]
        }
      }

      case 'delete_worker': {
        if (!params.worker_id)
          return { code: 500, message: "worker_id ko'rsatilmadi.", requests: [] }
        await deleteWorkerApi({ ids: [String(params.worker_id)] })
        return {
          code: 0,
          message: `Xodim (ID: ${params.worker_id}) muvaffaqiyatli o'chirildi.`,
          requests: [`POST /worker/delete [ID: ${params.worker_id}]`]
        }
      }

      case 'list_workers':
      case 'list_users': {
        const res = await getWorkerListApi({})
        const workers = (res.data as any)?.list || res.data || []
        return {
          code: 0,
          message: `${workers.length} ta xodim topildi.`,
          data: workers.map((w: any) => ({
            id: w.id,
            name: w.name,
            role: w.role,
            phone: w.phone,
            baseSalary: w.baseSalary
          })),
          requests: ['GET /worker/list']
        }
      }

      // ═══════════════════════════════════════════════════════
      // PRODUCTS  →  /product/*  +  /classifier/list
      // ═══════════════════════════════════════════════════════
      case 'create_product':
      case 'add_product_stock': {
        return await handleProductCreationOrUpdate(params, action === 'add_product_stock')
      }

      case 'update_product': {
        if (!params.product_id)
          return { code: 500, message: "product_id ko'rsatilmadi.", requests: [] }
        const payload: any = { id: String(params.product_id) }
        if (params.name) payload.productName = params.name
        if (params.price !== undefined) payload.price = Number(params.price)
        if (params.cost !== undefined) payload.cost = Number(params.cost)
        if (params.brand_name) payload.brand_name = params.brand_name
        if (params.quantity !== undefined) payload.quantityInStock = Number(params.quantity)
        if (params.expiration_date) payload.expiration_date = params.expiration_date
        const res = await saveProductApi(payload)
        return {
          code: 0,
          message: `Mahsulot muvaffaqiyatli yangilandi.`,
          data: res.data,
          requests: [`POST /product/save [ID: ${params.product_id}]`]
        }
      }

      case 'delete_product': {
        if (!params.product_id)
          return { code: 500, message: "product_id ko'rsatilmadi.", requests: [] }
        await deleteProductApi({ ids: [String(params.product_id)] })
        return {
          code: 0,
          message: `Mahsulot (ID: ${params.product_id}) o'chirildi.`,
          requests: [`POST /product/delete [ID: ${params.product_id}]`]
        }
      }

      case 'list_products':
      case 'search_product': {
        const query = params.search || params.query || params.name || ''
        const requestsList: string[] = []

        // 1. Search warehouse first by product name
        const res = await getProductListApi(query ? { productName: query } : {})
        requestsList.push(
          `GET /product/list${query ? '?productName=' + encodeURIComponent(query) : ''}`
        )
        let prods = (res.data as any)?.list || res.data || []

        // 2. Token-based full scan if not found by name
        if (query && !prods.length) {
          requestsList.push('GET /product/list [Full Scan]')
          const allRes = await getProductListApi({})
          const allList = (allRes.data as any)?.list || allRes.data || []
          const terms = query
            .toLowerCase()
            .split(/\s+/)
            .filter((t: string) => t.length > 0)
          prods = allList.filter((p: any) => {
            const fullText = `${(p.productName || p.name || '').toLowerCase()} ${(p.brand_name || '').toLowerCase()} ${(p.attribute_name || '').toLowerCase()}`
            return terms.some((t: string) => t.length > 1 && fullText.includes(t))
          })
        }

        // 3. ALWAYS search Milliy Mahsulotlar Bazasi when fewer than 3 warehouse results
        //    Even 1 generic match → still check national DB for specific variants
        let nationalResults: any[] = []
        if (query && prods.length < 3) {
          requestsList.push(
            `GET /classifier/list?search=${encodeURIComponent(query)}&page=1&page_size=20`
          )
          try {
            const classRes = await searchClassifierApi({ search: query, page: 1, page_size: 20 })
            nationalResults = classRes?.data || []
            // brand-word fallback if exact phrase gives nothing
            const term = query.toLowerCase().split(/\s+/)[0] || query
            if (!nationalResults.length && term !== query.toLowerCase()) {
              requestsList.push(
                `GET /classifier/list?search=${encodeURIComponent(term)}&page=1&page_size=20`
              )
              const brandRes = await searchClassifierApi({ search: term, page: 1, page_size: 20 })
              nationalResults = brandRes?.data || []
            }
          } catch (_) {
            // ignore
          }
        }

        // 4. Nothing found anywhere
        if (!prods.length && !nationalResults.length) {
          return {
            code: 0,
            message: `Omborda va Milliy Mahsulotlar Bazasida '${query}' topilmadi.`,
            data: [],
            requests: requestsList
          }
        }

        // 5. Build combined rich response
        const warehouseData = prods.map((p: any) => ({
          source: 'ombor',
          id: p.id,
          name: p.productName || p.name,
          brand: p.brand_name,
          SKU: p.SKU,
          price: p.price,
          cost: p.cost,
          quantity: p.quantityInStock,
          unit: p.unit,
          mxik_code: p.mxik_code,
          shtrix_code: p.shtrix_code,
          expiration_date: p.expiration_date
        }))

        const nationalData = nationalResults.slice(0, 8).map((c: any) => ({
          source: 'milliy_baza',
          classifier_id: c.id,
          name: `${c.mxik_name || ''}${c.attribute_name ? ' (' + c.attribute_name + ')' : ''}`,
          brand: c.brand_name,
          mxik_code: c.mxik_code,
          shtrix_code: c.shtrix_code,
          unit: c.unit
        }))

        const parts: string[] = []
        if (warehouseData.length) parts.push(`Omborda: ${warehouseData.length} ta`)
        if (nationalData.length) parts.push(`Milliy Bazada: ${nationalData.length} ta variant`)

        return {
          code: 0,
          message: `${parts.join('. ')}.`,
          data: { warehouse: warehouseData, national: nationalData },
          requests: requestsList
        }
      }

      // ═══════════════════════════════════════════════════════
      // DEPARTMENTS  →  /department/*
      // ═══════════════════════════════════════════════════════
      case 'create_department': {
        const res = await saveDepartmentApi({
          departmentName: params.name || "Yangi Bo'lim",
          remark: params.description
        })
        return {
          code: 0,
          message: `Bo'lim '${params.name}' yaratildi.`,
          data: res.data,
          requests: [`POST /department/save [Name: ${params.name}]`]
        }
      }

      case 'list_departments': {
        const res = await getDepartmentApi()
        const depts = (res.data as any)?.list || res.data || []
        return {
          code: 0,
          message: `${depts.length} ta bo'lim topildi.`,
          data: depts,
          requests: ['GET /department/list']
        }
      }

      // ═══════════════════════════════════════════════════════
      // POSITIONS & HR  →  /hr/*
      // ═══════════════════════════════════════════════════════
      case 'create_position': {
        const res = await savePositionApi({
          positionName: params.name || 'Yangi Lavozim',
          baseSalary: params.salary ? Number(params.salary) : 0,
          remark: params.description
        })
        return {
          code: 0,
          message: `Lavozim '${params.name}' yaratildi.`,
          data: res.data,
          requests: [`POST /hr/position/save [Name: ${params.name}]`]
        }
      }

      case 'list_positions': {
        const res = await getPositionListApi()
        return {
          code: 0,
          message: 'Lavozimlar olindi.',
          data: res.data,
          requests: ['GET /hr/position/list']
        }
      }

      case 'create_timesheet': {
        const res = await saveTimesheetApi(params)
        return {
          code: 0,
          message: `Davomat yaratildi.`,
          data: res.data,
          requests: ['POST /hr/timesheet/save']
        }
      }

      case 'create_staff_output': {
        const res = await saveOutputApi(params)
        return {
          code: 0,
          message: `Ishbay hajm kiritildi.`,
          data: res.data,
          requests: ['POST /hr/output/save']
        }
      }

      case 'list_staff_outputs': {
        const res = await getOutputListApi()
        return {
          code: 0,
          message: 'Ishbay yozuvlari olindi.',
          data: res.data,
          requests: ['GET /hr/output/list']
        }
      }

      case 'create_staff_adjustment': {
        const res = await saveAdjustmentApi(params)
        return {
          code: 0,
          message: `To'lov yozuvi kiritildi.`,
          data: res.data,
          requests: ['POST /hr/adjustment/save']
        }
      }

      case 'list_staff_adjustments': {
        const res = await getAdjustmentListApi()
        return {
          code: 0,
          message: "To'lovlar olindi.",
          data: res.data,
          requests: ['GET /hr/adjustment/list']
        }
      }

      // ═══════════════════════════════════════════════════════
      // SALARY  →  /salary/*  (real endpoints)
      // ═══════════════════════════════════════════════════════
      case 'list_salaries': {
        const res = await getSalaryListApi(params.worker_id ? { workerId: params.worker_id } : {})
        return {
          code: 0,
          message: "Oylik ro'yxati olindi.",
          data: (res.data as any)?.list || res.data || [],
          requests: ['GET /salary/list']
        }
      }

      case 'create_salary': {
        const res = await saveSalaryApi(params)
        return {
          code: 0,
          message: `Ish haqi yozuvi yaratildi.`,
          data: res.data,
          requests: ['POST /salary/save']
        }
      }

      case 'salary_payout': {
        const res = await bulkSalaryPayoutApi({
          workerIds: params.worker_ids || [],
          allowance: Number(params.allowance || 0),
          deduction: Number(params.deduction || 0),
          remark: params.remark
        })
        return {
          code: 0,
          message: `Oylik to'landi.`,
          data: res.data,
          requests: ['POST /salary/payout']
        }
      }

      // ═══════════════════════════════════════════════════════
      // SALES  →  /sales/*
      // ═══════════════════════════════════════════════════════
      case 'list_sales': {
        const res = await getSalesListApi({
          pageIndex: 1,
          pageSize: params.limit || 20,
          search: params.search,
          payment_method: params.payment_method,
          cashier_name: params.cashier_name
        })
        return {
          code: 0,
          message: 'Sotuvlar olindi.',
          data: (res.data as any)?.list || res.data || [],
          requests: ['GET /sales/list']
        }
      }

      case 'get_sale_receipt': {
        if (!params.receipt_number)
          return { code: 500, message: "receipt_number ko'rsatilmadi.", requests: [] }
        const res = await getSaleReceiptApi(params.receipt_number)
        return {
          code: 0,
          message: `Chek #${params.receipt_number} olindi.`,
          data: res.data,
          requests: [`GET /sales/receipt/${params.receipt_number}`]
        }
      }

      case 'list_debtors': {
        const res = await getDebtorsApi(params.search ? { search: params.search } : {})
        return {
          code: 0,
          message: "Qarzdorlar ro'yxati olindi.",
          data: (res.data as any)?.list || res.data || [],
          requests: ['GET /sales/debtors']
        }
      }

      case 'repay_debt': {
        if (!params.customer_name || !params.amount) {
          return { code: 500, message: 'customer_name va amount majburiy.', requests: [] }
        }
        const res = await repayDebtApi({
          customer_name: params.customer_name,
          customer_phone: params.customer_phone,
          amount: Number(params.amount),
          payment_method: params.payment_method || 'naqd',
          remark: params.remark
        })
        return {
          code: 0,
          message: `${params.customer_name} ning qarzi ${params.amount} so'mga qaytarildi.`,
          data: res.data,
          requests: ['POST /sales/repay-debt']
        }
      }

      // ═══════════════════════════════════════════════════════
      // BRANCH  →  /branch/*
      // ═══════════════════════════════════════════════════════
      case 'list_branches': {
        const res = await getBranchListApi()
        return {
          code: 0,
          message: "Filiallar ro'yxati olindi.",
          data: (res as any)?.data?.data || (res as any)?.data || [],
          requests: ['GET /branch/list']
        }
      }

      case 'create_branch': {
        const res = await saveBranchApi({
          name: params.name,
          address: params.address,
          phone: params.phone,
          code: params.code
        })
        return {
          code: 0,
          message: `Filial '${params.name}' yaratildi.`,
          data: res.data,
          requests: ['POST /branch/save']
        }
      }

      // ═══════════════════════════════════════════════════════
      // ROLES  →  /role/*  (real endpoints)
      // ═══════════════════════════════════════════════════════
      case 'list_roles': {
        const res = await getRoleListApi()
        return {
          code: 0,
          message: 'Rollar olindi.',
          data: (res.data as any)?.list || res.data || [],
          requests: ['GET /role/list']
        }
      }

      case 'create_role': {
        const res = await saveRoleApi({
          roleName: params.name,
          remark: params.remark,
          permissions: params.permissions || []
        })
        return {
          code: 0,
          message: `Rol '${params.name}' yaratildi.`,
          data: res.data,
          requests: [`POST /role/save [Role: ${params.name}]`]
        }
      }

      case 'delete_role': {
        await deleteRoleApi({ id: String(params.role_id) })
        return {
          code: 0,
          message: `Rol o'chirildi.`,
          requests: [`POST /role/delete [ID: ${params.role_id}]`]
        }
      }

      // ═══════════════════════════════════════════════════════
      // CUTTING / PRODUCTION  →  /cutting/*
      // ═══════════════════════════════════════════════════════
      case 'list_cutting_orders': {
        const res = await getOrderListApi()
        return {
          code: 0,
          message: 'Buyurtmalar olindi.',
          data: res.data,
          requests: ['GET /cutting/order/list']
        }
      }

      case 'create_cutting_order': {
        const res = await saveOrderApi({
          order_number: params.order_number || `ORD-${Math.floor(Math.random() * 899999 + 100000)}`,
          project: params.project || '',
          order_name: params.order_name || '',
          items: params.items || []
        })
        return {
          code: 0,
          message: `Buyurtma yaratildi.`,
          data: res.data,
          requests: ['POST /cutting/order/save']
        }
      }

      case 'delete_cutting_order': {
        await deleteOrderApi({ ids: [String(params.order_id)] })
        return {
          code: 0,
          message: `Raskroy buyurtmasi o'chirildi.`,
          requests: [`POST /cutting/order/delete [ID: ${params.order_id}]`]
        }
      }

      case 'start_production': {
        const res = await startProductionApi({ orderId: String(params.order_id) })
        return {
          code: 0,
          message: `Ishlab chiqarish boshlandi.`,
          data: res.data,
          requests: [`POST /cutting/order/start-production [ID: ${params.order_id}]`]
        }
      }

      case 'list_cutting_tasks': {
        const res = await getTaskListApi()
        return {
          code: 0,
          message: 'Topshiriqlar olindi.',
          data: res.data,
          requests: ['GET /cutting/task/list']
        }
      }

      case 'update_task_status': {
        const res = await updateTaskStatusApi({
          taskId: String(params.task_id),
          status: params.status
        })
        return {
          code: 0,
          message: `Topshiriq holati yangilandi.`,
          data: res.data,
          requests: [`POST /cutting/task/update-status`]
        }
      }

      // ═══════════════════════════════════════════════════════
      // DEVICE PUSH  →  /sales/pending-pushes
      // ═══════════════════════════════════════════════════════
      case 'list_pending_pushes': {
        const res = await getPendingSalesPushApi()
        return {
          code: 0,
          message: 'Kutayotgan pushlar olindi.',
          data: res.data,
          requests: ['GET /sales/pending-pushes']
        }
      }

      case 'respond_push': {
        const res = await respondSalesPushApi(params.push_id, params.action || 'accept')
        return {
          code: 0,
          message: `Push habari ${params.action === 'accept' ? 'qabul qilindi' : 'rad etildi'}.`,
          data: res.data,
          requests: [`POST /sales/respond-push [PushID: ${params.push_id}]`]
        }
      }

      // ═══════════════════════════════════════════════════════
      // QR CODES  →  /qr/*
      // ═══════════════════════════════════════════════════════
      case 'generate_qr_code': {
        const res = await saveQrApi({
          taskId: String(params.task_id),
          quantity: Number(params.quantity || 1)
        })
        return {
          code: 0,
          message: `QR kod generatsiya qilindi.`,
          data: res.data,
          requests: ['POST /qr/save']
        }
      }

      case 'list_qr_codes': {
        const res = await getQrListApi()
        return { code: 0, message: 'QR kodlar olindi.', data: res.data, requests: ['GET /qr/list'] }
      }

      case 'delete_qr_code': {
        await deleteQrApi({ ids: [String(params.qr_id)] })
        return {
          code: 0,
          message: `QR kod o'chirildi.`,
          requests: [`POST /qr/delete [ID: ${params.qr_id}]`]
        }
      }

      // ═══════════════════════════════════════════════════════
      // ANALYTICS & REPORTS
      // ═══════════════════════════════════════════════════════
      case 'get_top_selling_products': {
        const res = await request.get({ url: '/sales/top-selling' })
        const list = res.data || []
        const summary = list
          .map(
            (it: any, idx: number) =>
              `${idx + 1}. ${it.name}: ${it.quantity} dona ($${Number(it.revenue || 0).toLocaleString()})`
          )
          .join('\n')
        return {
          code: 0,
          message: `🏆 Eng ko'p sotilgan tovarlar:\n${summary || "Hozircha sotuvlar ma'lumoti yo'q."}`,
          data: list,
          requests: ['GET /sales/top-selling']
        }
      }

      case 'get_sales_analytics': {
        const res = await request.get({ url: '/sales/analytics' })
        const data = res.data || {}
        return {
          code: 0,
          message: `📊 Savdo tahlili: Jami ${data.total_sales || 0} ta sotuv, $${Number(data.total_revenue || 0).toLocaleString()} umumiy aylanma.`,
          data: data,
          requests: ['GET /sales/analytics']
        }
      }

      case 'get_debt_report': {
        const res = await getDebtorsApi({})
        const d = res.data || {}
        return {
          code: 0,
          message: `📌 Nasiyalar: Jami qarz $${Number(d.total_debt || 0).toLocaleString()}, faol qarzdorlar: ${d.active_debtors_count || 0} ta.`,
          data: d,
          requests: ['GET /sales/debtors']
        }
      }

      default:
        return { code: 500, message: `'${action}' nomli noma'lum amal.`, requests: [] }
    }
  } catch (err: any) {
    console.error(`[AI Dispatcher] Error during ${action}:`, err)
    return {
      code: 500,
      message:
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err.message ||
        'Server xatoligi.',
      requests: [`ERROR /api/${action}`]
    }
  }
}

export async function dispatchAIFunction(action: string, params: any): Promise<AIDispatchResult> {
  const res = await _dispatchAIFunctionInternal(action, params)
  if (res && res.code === 0) {
    notifyDataUpdated(action, params)
  }
  return res
}
