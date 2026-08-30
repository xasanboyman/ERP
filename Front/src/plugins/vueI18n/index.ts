import type { App } from 'vue'
import { createI18n } from 'vue-i18n'
import { useLocaleStoreWithOut } from '@/store/modules/locale'
import type { I18n, I18nOptions } from 'vue-i18n'
import { setHtmlPageLang } from './helper'
import uz from '@/locales/uz'
import cr from '@/locales/cr'
import en from '@/locales/en'

export let i18n: ReturnType<typeof createI18n>

const localeMessages: Record<string, any> = {
  uz,
  cr,
  en
}

const createI18nOptions = (): I18nOptions => {
  const localeStore = useLocaleStoreWithOut()
  const locale = localeStore.getCurrentLocale
  const localeMap = localeStore.getLocaleMap
  const message = localeMessages[locale.lang] || uz

  setHtmlPageLang(locale.lang)

  localeStore.setCurrentLocale({
    lang: locale.lang
  })

  return {
    legacy: false,
    locale: locale.lang,
    fallbackLocale: locale.lang,
    messages: {
      [locale.lang]: message
    },
    availableLocales: localeMap.map((v) => v.lang),
    sync: true,
    silentTranslationWarn: true,
    missingWarn: false,
    silentFallbackWarn: true
  }
}

export const setupI18n = (app: App<Element>) => {
  const options = createI18nOptions()
  i18n = createI18n(options) as I18n
  app.use(i18n)
}
