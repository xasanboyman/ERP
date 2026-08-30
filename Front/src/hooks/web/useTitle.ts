import { watch, ref } from 'vue'
import { isString } from '@/utils/is'
import { useAppStoreWithOut } from '@/store/modules/app'
import { useI18n } from '@/hooks/web/useI18n'

export const useTitle = (newTitle?: string) => {
  const { t } = useI18n()
  const appStore = useAppStoreWithOut()

  const baseTitle = appStore.getTitle || 'ERP System'
  const pageTitle = newTitle ? t(newTitle as string) : ''
  const displayTitle =
    pageTitle && pageTitle !== 'undefined' ? `${baseTitle} - ${pageTitle}` : baseTitle

  const title = ref(displayTitle)

  watch(
    title,
    (n, o) => {
      if (isString(n) && n !== o && document) {
        document.title = n
      }
    },
    { immediate: true }
  )

  return title
}
