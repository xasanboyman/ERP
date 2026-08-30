import { defineStore } from 'pinia'
import { store } from '../index'
import uzUz from 'element-plus/es/locale/lang/uz-uz'
import en from 'element-plus/es/locale/lang/en'
import crEl from '@/utils/element-cr'
import { useStorage } from '@/hooks/web/useStorage'
import { LocaleDropdownType } from '@/components/LocaleDropdown'

const { getStorage, setStorage } = useStorage('localStorage')

const elLocaleMap: Record<string, any> = {
  uz: uzUz,
  cr: crEl,
  en: en
}
interface LocaleState {
  currentLocale: LocaleDropdownType
  localeMap: LocaleDropdownType[]
}

export const useLocaleStore = defineStore('locales', {
  state: (): LocaleState => {
    const storedLang = getStorage('lang')
    const lang =
      storedLang === 'uz' || storedLang === 'cr' || storedLang === 'en' ? storedLang : 'uz'
    return {
      currentLocale: {
        lang: lang,
        elLocale: elLocaleMap[lang]
      },
      // Languages
      localeMap: [
        {
          lang: 'uz',
          name: "O'zbekcha (Lotin)"
        },
        {
          lang: 'cr',
          name: 'Ўзбекча (Кирилл)'
        },
        {
          lang: 'en',
          name: 'English'
        }
      ]
    }
  },
  getters: {
    getCurrentLocale(): LocaleDropdownType {
      return this.currentLocale
    },
    getLocaleMap(): LocaleDropdownType[] {
      return this.localeMap
    }
  },
  actions: {
    setCurrentLocale(localeMap: LocaleDropdownType) {
      // this.locale = Object.assign(this.locale, localeMap)
      this.currentLocale.lang = localeMap?.lang
      this.currentLocale.elLocale = elLocaleMap[localeMap?.lang]
      setStorage('lang', localeMap?.lang)
    }
  }
})

export const useLocaleStoreWithOut = () => {
  return useLocaleStore(store)
}
