import { i18n } from '@/plugins/vueI18n'
import { toCyrillic } from '@/utils/transliterate'

type I18nGlobalTranslation = {
  (key: string): string
  (key: string, locale: string): string
  (key: string, locale: string, list: unknown[]): string
  (key: string, locale: string, named: Record<string, unknown>): string
  (key: string, list: unknown[]): string
  (key: string, named: Record<string, unknown>): string
}

type I18nTranslationRestParameters = [string, any]

const getKey = (namespace: string | undefined, key: string) => {
  if (!namespace) {
    return key
  }
  if (key.startsWith(namespace)) {
    return key
  }
  return `${namespace}.${key}`
}

export const useI18n = (
  namespace?: string
): {
  t: I18nGlobalTranslation
} => {
  const normalFn = {
    t: (key: string) => {
      return getKey(namespace, key)
    }
  }

  if (!i18n) {
    return normalFn
  }

  const { t, ...methods } = i18n.global

  const tFn: I18nGlobalTranslation = (key: string, ...arg: any[]) => {
    if (!key) return ''
    const currentLang = (i18n.global.locale as any)?.value || (i18n.global as any).locale || 'uz'

    if (!key.includes('.') && !namespace) {
      if (currentLang === 'cr') {
        return toCyrillic(key)
      }
      return key
    }

    const fullKey = getKey(namespace, key)
    const res = (t as any)(fullKey, ...(arg as I18nTranslationRestParameters))
    if (res === fullKey || !res) {
      if (currentLang === 'cr') {
        return key.includes('.') ? key : toCyrillic(key)
      }
      return key
    }
    return res
  }
  return {
    ...methods,
    t: tFn
  }
}

export const t = (key: string) => {
  if (!i18n) return key
  const currentLang = (i18n.global.locale as any)?.value || (i18n.global as any).locale || 'uz'
  if (currentLang === 'cr') {
    return toCyrillic(key)
  }
  return key
}
