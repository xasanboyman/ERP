/**
 *
 * @param component 需要注册的组件
 * @param alias 组件别名
 * @returns any
 */
export const withInstall = <T>(component: T, alias?: string) => {
  const comp = component as any
  comp.install = (app: any) => {
    app.component(comp.name || comp.displayName, component)
    if (alias) {
      app.config.globalProperties[alias] = component
    }
  }
  return component as T & Plugin
}

/**
 * @param str 需要转下划线的驼峰字符串
 * @returns 字符串下划线
 */
export const humpToUnderline = (str: string): string => {
  return str.replace(/([A-Z])/g, '-$1').toLowerCase()
}

/**
 * @param str 需要转驼峰的下划线字符串
 * @returns 字符串驼峰
 */
export const underlineToHump = (str: string): string => {
  if (!str) return ''
  return str.replace(/\-(\w)/g, (_, letter: string) => {
    return letter.toUpperCase()
  })
}

/**
 * 驼峰转横杠
 */
export const humpToDash = (str: string): string => {
  return str.replace(/([A-Z])/g, '-$1').toLowerCase()
}

export const setCssVar = (prop: string, val: any, dom = document.documentElement) => {
  dom.style.setProperty(prop, val)
}

export const getCssVar = (prop: string, dom = document.documentElement) => {
  return getComputedStyle(dom).getPropertyValue(prop)
}

/**
 * 查找数组对象的某个下标
 * @param {Array} ary 查找的数组
 * @param {Functon} fn 判断的方法
 */
export const findIndex = <T = Recordable>(ary: Array<T>, fn: Fn): number => {
  if (ary.findIndex) {
    return ary.findIndex(fn)
  }
  let index = -1
  ary.some((item: T, i: number, ary: Array<T>) => {
    const ret: T = fn(item, i, ary)
    if (ret) {
      index = i
      return ret
    }
  })
  return index
}

export const trim = (str: string) => {
  return str.replace(/(^\s*)|(\s*$)/g, '')
}

/**
 * @param {Date | number | string} time 需要转换的时间
 * @param {String} fmt 需要转换的格式 如 yyyy-MM-dd、yyyy-MM-dd HH:mm:ss
 */
/**
 * Formats a number with space grouping for thousands (e.g. 1 000 000 or 6 000)
 */
export function formatMoney(val: number | string | null | undefined, decimals = 0): string {
  if (val === null || val === undefined || val === '') return '0'
  const cleanStr = typeof val === 'string' ? val.replace(/\s+/g, '').replace(/[^\d.-]/g, '') : val
  const num = Number(cleanStr)
  if (isNaN(num)) return '0'
  const isNegative = num < 0
  const absNum = Math.abs(num)
  const hasCents = Math.abs(absNum % 1) > 0.0001
  const dec = decimals > 0 ? decimals : hasCents ? 2 : 0
  const parts = absNum.toFixed(dec).split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  const result = dec > 0 && parts[1] && parts[1] !== '00' ? parts.join('.') : parts[0]
  return isNegative ? `-${result}` : result
}

export function moneyFormatter(value: any): string {
  if (value === null || value === undefined || value === '') return ''
  const cleanStr = String(value)
    .replace(/\s+/g, '')
    .replace(/[^\d.-]/g, '')
  const num = Number(cleanStr)
  if (isNaN(num)) return String(value)
  const isNegative = num < 0
  const absNum = Math.abs(num)
  const hasCents = Math.abs(absNum % 1) > 0.0001
  const parts = hasCents ? absNum.toFixed(2).split('.') : [Math.round(absNum).toString()]
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  const formatted = parts.length > 1 && parts[1] && parts[1] !== '00' ? parts.join('.') : parts[0]
  return isNegative ? `-${formatted}` : formatted
}

export function moneyParser(value: string): string {
  if (!value) return ''
  return String(value)
    .replace(/\s+/g, '')
    .replace(/[^\d.-]/g, '')
}

/**
 * 生成随机字符串
 */
export function toAnyString() {
  const str: string = 'xxxxx-xxxxx-4xxxx-yxxxx-xxxxx'.replace(/[xy]/g, (c: string) => {
    const r: number = (Math.random() * 16) | 0
    const v: number = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString()
  })
  return str
}

/**
 * 首字母大写
 */
export function firstUpperCase(str: string) {
  return str.toLowerCase().replace(/( |^)[a-z]/g, (L) => L.toUpperCase())
}

/**
 * 把对象转为formData
 */
export function objToFormData(obj: Recordable) {
  const formData = new FormData()
  Object.keys(obj).forEach((key) => {
    formData.append(key, obj[key])
  })
  return formData
}
