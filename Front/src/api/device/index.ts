import request from '@/axios'

export interface DeviceTokenItem {
  id: number
  user_id: number
  device_name: string
  token: string
  pair_code: string
  status: 'active' | 'revoked' | 'expired'
  created_at?: string
  last_used_at?: string
  expires_at?: string
}

export interface PairDeviceRequest {
  device_name: string
  user_id?: number
}

export interface SalesPushItem {
  product_id: string
  product_name: string
  quantity: number
  price: number
  cost?: number
  shtrix_code?: string
}

export interface SalesPushCreate {
  pc_user_id: number
  items: SalesPushItem[]
}

export interface PhoneCheckoutRequest {
  payment_type: 'cash' | 'card' | 'debt' | 'naqd' | 'karta' | 'nasiya'
  items: SalesPushItem[]
  total_amount: number
  paid_amount?: number
  discount?: number
  customer_name?: string
  customer_phone?: string
  remark?: string
}

// 1. Create Pairing QR Code & Token
export const pairDeviceTokenApi = (data: PairDeviceRequest) => {
  return request.post({ url: '/api/device/pair-token', data })
}

// 2. List user's paired devices
export const listDeviceTokensApi = () => {
  return request.get({ url: '/api/device/list' })
}

// 3. Revoke a device token
export const revokeDeviceTokenApi = (deviceId: number) => {
  return request.delete({ url: `/api/device/revoke/${deviceId}` })
}

// 4. Verify token from mobile device
export const verifyDeviceTokenApi = (deviceToken: string) => {
  return request.get({
    url: '/api/device/verify',
    headers: {
      'X-Device-Token': deviceToken
    }
  })
}

// 5. Mobile Push Sale to PC
export const pushPcSaleApi = (data: SalesPushCreate, deviceToken: string) => {
  return request.post({
    url: '/api/sales/push-pc-sale',
    data,
    headers: {
      'X-Device-Token': deviceToken
    }
  })
}

// 6. PC get pending sales pushes
export const getPendingSalesPushApi = () => {
  return request.get({ url: '/api/sales/pending-pushes' })
}

// 7. Respond to Sales Push (Accept or Decline)
export const respondSalesPushApi = (pushId: string, action: 'accept' | 'decline') => {
  return request.post({
    url: '/api/sales/respond-push',
    data: { push_id: pushId, action }
  })
}

// 8. Get Push Payload for POS Cart Pre-fill
export const getPushPayloadApi = (pushId: string) => {
  return request.get({ url: `/api/sales/push-payload/${pushId}` })
}

// 9. Mobile Phone POS Standalone Checkout
export const phoneCheckoutApi = (data: PhoneCheckoutRequest, deviceToken: string) => {
  return request.post({
    url: '/api/sales/phone-checkout',
    data,
    headers: {
      'X-Device-Token': deviceToken
    }
  })
}

// 10. High-performance Python zxingcpp frame decoder API
export const decodeFrameApi = (base64Image: string) => {
  return request.post({
    url: '/api/device/decode-frame',
    data: { base64_image: base64Image }
  })
}
