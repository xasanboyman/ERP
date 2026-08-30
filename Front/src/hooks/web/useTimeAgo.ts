import { useTimeAgo as useTimeAgoCore, UseTimeAgoMessages } from '@vueuse/core'
import { computed, unref } from 'vue'
import { useLocaleStoreWithOut } from '@/store/modules/locale'

const TIME_AGO_MESSAGE_MAP: {
  uz: UseTimeAgoMessages
  cr: UseTimeAgoMessages
  en: UseTimeAgoMessages
} = {
  uz: {
    justNow: 'Hozirgina',
    invalid: 'Noto‘g‘ri sana',
    past: (n) => (n.match(/\d/) ? `${n} oldin` : n),
    future: (n) => (n.match(/\d/) ? `${n} keyin` : n),
    month: (n, past) => (n === 1 ? (past ? 'o‘tgan oy' : 'keyingi oy') : `${n} oy`),
    year: (n, past) => (n === 1 ? (past ? 'o‘tgan yil' : 'keyingi yil') : `${n} yil`),
    day: (n, past) => (n === 1 ? (past ? 'kecha' : 'ertaga') : `${n} kun`),
    week: (n, past) => (n === 1 ? (past ? 'o‘tgan hafta' : 'keyingi hafta') : `${n} hafta`),
    hour: (n) => `${n} soat`,
    minute: (n) => `${n} daqiqa`,
    second: (n) => `${n} soniya`
  },
  cr: {
    justNow: 'Ҳозиргина',
    invalid: 'Нотўғри сана',
    past: (n) => (n.match(/\d/) ? `${n} олдин` : n),
    future: (n) => (n.match(/\d/) ? `${n} кейин` : n),
    month: (n, past) => (n === 1 ? (past ? 'ўтган ой' : 'кейинги ой') : `${n} ой`),
    year: (n, past) => (n === 1 ? (past ? 'ўтган йил' : 'кейинги йил') : `${n} йил`),
    day: (n, past) => (n === 1 ? (past ? 'кеча' : 'эртага') : `${n} кун`),
    week: (n, past) => (n === 1 ? (past ? 'ўтган ҳафта' : 'кейинги ҳафта') : `${n} ҳафта`),
    hour: (n) => `${n} соат`,
    minute: (n) => `${n} дақиқа`,
    second: (n) => `${n} сония`
  },
  en: {
    justNow: 'just now',
    invalid: 'Invalid Date',
    past: (n) => (n.match(/\d/) ? `${n} ago` : n),
    future: (n) => (n.match(/\d/) ? `in ${n}` : n),
    month: (n, past) =>
      n === 1 ? (past ? 'last month' : 'next month') : `${n} month${n > 1 ? 's' : ''}`,
    year: (n, past) =>
      n === 1 ? (past ? 'last year' : 'next year') : `${n} year${n > 1 ? 's' : ''}`,
    day: (n, past) => (n === 1 ? (past ? 'yesterday' : 'tomorrow') : `${n} day${n > 1 ? 's' : ''}`),
    week: (n, past) =>
      n === 1 ? (past ? 'last week' : 'next week') : `${n} week${n > 1 ? 's' : ''}`,
    hour: (n) => `${n} hour${n > 1 ? 's' : ''}`,
    minute: (n) => `${n} minute${n > 1 ? 's' : ''}`,
    second: (n) => `${n} second${n > 1 ? 's' : ''}`
  }
}

export const useTimeAgo = (time: Date | number | string) => {
  const localeStore = useLocaleStoreWithOut()

  const currentLocale = computed(() => localeStore.getCurrentLocale)

  const timeAgo = useTimeAgoCore(time, {
    messages: TIME_AGO_MESSAGE_MAP[unref(currentLocale).lang]
  })

  return timeAgo
}
