import { i18n } from '@/plugins/vueI18n'
import { useLocaleStoreWithOut } from '@/store/modules/locale'
import { setHtmlPageLang } from '@/plugins/vueI18n/helper'
import uz from '@/locales/uz'
import cr from '@/locales/cr'
import en from '@/locales/en'

const localeMap: Record<string, any> = {
  uz,
  cr,
  en
}

const setI18nLanguage = (locale: LocaleType) => {
  const localeStore = useLocaleStoreWithOut()

  if (i18n.mode === 'legacy') {
    i18n.global.locale = locale
  } else {
    ;(i18n.global.locale as any).value = locale
  }
  localeStore.setCurrentLocale({
    lang: locale
  })
  setHtmlPageLang(locale)
}

export const useLocale = () => {
  // Switching the language will change the locale of useI18n
  // And submit to configuration modification
  const changeLocale = async (locale: LocaleType) => {
    const globalI18n = i18n.global
    const msg = localeMap[locale] || uz
    globalI18n.setLocaleMessage(locale, msg)
    setI18nLanguage(locale)
  }

  return {
    changeLocale
  }
}
