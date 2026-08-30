import request from '@/axios'

export const getQrListApi = () => {
  return request.get({ url: '/qr/list' })
}

export const saveQrApi = (data: { taskId: string; quantity: number }) => {
  return request.post({ url: '/qr/save', data })
}

export const deleteQrApi = (data: { ids: string[] }) => {
  return request.post({ url: '/qr/delete', data })
}
