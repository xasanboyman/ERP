<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
const { t } = useI18n()
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@/components/Icon'
import {
  ElButton,
  ElInput,
  ElCard,
  ElTag,
  ElMessage,
  ElDialog,
  ElForm,
  ElFormItem,
  ElSelect,
  ElOption,
  ElRadioGroup,
  ElRadioButton
} from 'element-plus'
import {
  verifyDeviceTokenApi,
  pushPcSaleApi,
  phoneCheckoutApi,
  decodeFrameApi,
  SalesPushItem
} from '@/api/device'
import { getWorkerListApi } from '@/api/worker'
import { getProductByBarcodeApi } from '@/api/product'
import {
  getProductMainImage,
  getProductFallbackAvatar,
  handleImageError
} from '@/utils/productImages'
import { formatMoney } from '@/utils'

const route = useRoute()
const router = useRouter()

const deviceToken = ref(localStorage.getItem('X-Device-Token') || '')
const deviceStatus = ref<'checking' | 'unpaired' | 'paired'>('checking')
const deviceName = ref('Mobil Skaner')

// Mode selection
const currentMode = ref<'pc' | 'phone'>('pc') // 'pc' = PC Sale, 'phone' = Phone Sale

// Camera Scanner state
const isCameraActive = ref(false)
const lastScannedCode = ref('')
const lastDetectedBarcode = ref('')
const lastDetectedFormat = ref('')
const scannerStatus = ref('Kamera tayyor')
let lastScanTime = 0
let pythonScanTimer: any = null
let scannerStream: MediaStream | null = null

// Controls state
const isTorchSupported = ref(false)
const isTorchActive = ref(false)
const scanSuccessFlash = ref(false)

const toggleCameraScanner = () => {
  if (isCameraActive.value) {
    stopCameraScanner()
  } else {
    startCameraScanner()
  }
}

const playBeepSound = () => {
  try {
    if (navigator.vibrate) {
      navigator.vibrate(120)
    }
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
    if (AudioContextClass) {
      const ctx = new AudioContextClass()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.type = 'sine'
      osc.frequency.setValueAtTime(1760, ctx.currentTime)
      gain.gain.setValueAtTime(0.3, ctx.currentTime)
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.18)
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start()
      osc.stop(ctx.currentTime + 0.18)
    }
  } catch (e) {
    void e
  }
}

const triggerFlashEffect = () => {
  scanSuccessFlash.value = true
  setTimeout(() => {
    scanSuccessFlash.value = false
  }, 500)
}

const startPythonFrameScanner = (videoElem: HTMLVideoElement) => {
  if (pythonScanTimer) clearInterval(pythonScanTimer)
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  let isSending = false

  pythonScanTimer = setInterval(async () => {
    if (!isCameraActive.value || isSending || !videoElem || !videoElem.videoWidth) return
    try {
      isSending = true
      const vW = videoElem.videoWidth || 1280
      const vH = videoElem.videoHeight || 720

      // Preserve the entire barcode, including its quiet zones and check digit.
      const scale = Math.min(1, 1280 / vW)
      canvas.width = Math.round(vW * scale)
      canvas.height = Math.round(vH * scale)
      ctx?.drawImage(videoElem, 0, 0, vW, vH, 0, 0, canvas.width, canvas.height)

      const base64Data = canvas.toDataURL('image/jpeg', 0.92)

      const res = (await decodeFrameApi(base64Data)) as any
      if (res && res.code === 0 && res.barcode) {
        const text = String(res.barcode).trim()
        lastDetectedBarcode.value = text
        lastDetectedFormat.value = res.format || ''
        const now = Date.now()
        if (
          text &&
          !scanLoading.value &&
          (text !== lastScannedCode.value || now - lastScanTime > 1500)
        ) {
          lastScannedCode.value = text
          lastScanTime = now
          playBeepSound()
          triggerFlashEffect()
          onCameraScanSuccess(text)
        }
      } else {
        scannerStatus.value = 'Kod topilmadi - shtrix-kodni fokusga oling'
      }
    } catch (e) {
      scannerStatus.value = "Kodni tekshirib bo'lmadi"
    } finally {
      isSending = false
    }
  }, 350)
}

const syncScannerTrackCapabilities = async (stream: MediaStream | null) => {
  scannerStream = stream
  const track = scannerStream?.getVideoTracks()[0]
  const caps = track?.getCapabilities?.() as any
  isTorchSupported.value = Boolean(caps?.torch)
  if (caps?.focusMode?.includes?.('continuous')) {
    await track
      ?.applyConstraints({ advanced: [{ focusMode: 'continuous' } as any] })
      .catch(() => undefined)
  }
}

const startCameraScanner = async () => {
  await stopCameraScanner(false)
  isCameraActive.value = true
  lastScannedCode.value = ''
  lastDetectedBarcode.value = ''
  lastDetectedFormat.value = ''
  scannerStatus.value = 'Kamera tayyor'
  lastScanTime = 0
  await nextTick()

  try {
    const targetContainer = document.querySelector('#interactive-viewport') as HTMLElement
    if (!targetContainer) throw new Error('Camera preview element was not mounted')
    if (!navigator.mediaDevices?.getUserMedia) {
      if (!window.isSecureContext && location.protocol !== 'https:') {
        throw new Error(
          `Camera requires HTTPS. Open https://${location.host}${location.pathname}${location.hash}`
        )
      }
      throw new Error('Camera API is not available in this browser')
    }

    targetContainer.replaceChildren()
    const videoElem = document.createElement('video')
    videoElem.className = 'scanner-camera'
    videoElem.autoplay = true
    videoElem.muted = true
    videoElem.playsInline = true
    targetContainer.appendChild(videoElem)

    scannerStream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    })
    videoElem.srcObject = scannerStream
    await videoElem.play()

    await syncScannerTrackCapabilities(scannerStream)
    scannerStatus.value = 'Kodni qidiryapti'
    startPythonFrameScanner(videoElem)
  } catch (err: any) {
    console.error('Camera startup error:', err)
    ElMessage.error(err?.message || 'Kamerani ochishda xatolik. Kamera ruxsatini tekshiring.')
    await stopCameraScanner()
  }
}

const toggleTorch = async () => {
  try {
    const track = scannerStream?.getVideoTracks()[0]
    if (!track) return
    isTorchActive.value = !isTorchActive.value
    await track.applyConstraints({ advanced: [{ torch: isTorchActive.value } as any] })
  } catch (e) {
    console.error('Torch toggle error:', e)
  }
}

const stopCameraScanner = async (markInactive = true) => {
  if (pythonScanTimer) {
    clearInterval(pythonScanTimer)
    pythonScanTimer = null
  }
  if (scannerStream) {
    scannerStream.getTracks().forEach((track) => track.stop())
    scannerStream = null
  }
  const targetContainer = document.querySelector('#interactive-viewport') as HTMLElement
  if (targetContainer) {
    targetContainer.replaceChildren()
  }
  isTorchActive.value = false
  isTorchSupported.value = false
  if (markInactive) isCameraActive.value = false
}

const onCameraScanSuccess = (decodedText: string) => {
  if (!decodedText) return

  // Check if scanning an auto-pairing URL or code while unpaired
  if (decodedText.includes('pair_code=') || decodedText.startsWith('PAIR-')) {
    let pairCode = decodedText
    if (decodedText.includes('pair_code=')) {
      pairCode = decodedText.split('pair_code=')[1]?.split('&')[0] || decodedText
    }
    pairCodeInput.value = pairCode.trim()
    savePairToken()
    stopCameraScanner()
    return
  }

  // If paired, treat decodedText as product barcode or QR code
  barcodeInput.value = decodedText.trim()
  addScannedItem()
}

// Scanner state
const barcodeInput = ref('')
const quantityInput = ref(1)
const cartItems = ref<SalesPushItem[]>([])

// Pair pairing input
const pairCodeInput = ref('')

const checkDeviceAuth = async () => {
  if (!deviceToken.value) {
    deviceStatus.value = 'unpaired'
    return
  }
  try {
    const res = await verifyDeviceTokenApi(deviceToken.value)
    if (res && (res.code === 0 || res.data)) {
      deviceStatus.value = 'paired'
      deviceName.value = res.data?.device_name || 'Mobil Skaner'
      if (res.data?.token) {
        deviceToken.value = res.data.token
        localStorage.setItem('X-Device-Token', res.data.token)
      }
    } else {
      localStorage.removeItem('X-Device-Token')
      deviceToken.value = ''
      deviceStatus.value = 'unpaired'
    }
  } catch (err) {
    localStorage.removeItem('X-Device-Token')
    deviceToken.value = ''
    deviceStatus.value = 'unpaired'
  }
}

const savePairToken = () => {
  if (!pairCodeInput.value.trim()) {
    ElMessage.warning('Ulash kodini kiriting!')
    return
  }
  deviceToken.value = pairCodeInput.value.trim()
  localStorage.setItem('X-Device-Token', deviceToken.value)
  checkDeviceAuth()
}

const scanLoading = ref(false)

// Add item to cart with real product lookup
const addScannedItem = async () => {
  if (!barcodeInput.value.trim()) {
    ElMessage.warning('Shtrix-kodni kiriting!')
    return
  }
  if (scanLoading.value) return

  const code = barcodeInput.value.trim()
  const qty = quantityInput.value || 1

  try {
    scanLoading.value = true
    const res = await getProductByBarcodeApi(code)
    const prodData = res?.data as any
    if (res?.code !== 0 || !prodData?.id) {
      ElMessage.warning(`Shtrix-kod topilmadi: ${code}`)
      barcodeInput.value = ''
      return
    }

    const pId = prodData.product_id || prodData.id
    const pName = prodData.product_name || prodData.productName
    const selectedPkg = prodData.selected_packaging
    const pPrice = Number(selectedPkg ? selectedPkg.price : prodData.price || 0)
    const pUnitName = selectedPkg ? selectedPkg.unit_name : prodData.unit || 'kg'
    const pConversionFactor = selectedPkg ? selectedPkg.conversion_factor || 1.0 : 1.0
    const pShtrix = selectedPkg?.shtrix_code || prodData?.shtrix_code || code
    const pMxik = prodData?.mxik_code || ''
    const pImage = prodData?.image_url || ''
    const pBrand = prodData?.brand_name || ''

    const existing = cartItems.value.find(
      (it) =>
        (it.product_id === String(pId) || it.shtrix_code === pShtrix) &&
        (it as any).unit_name === pUnitName
    )
    if (existing) {
      existing.quantity += qty
    } else {
      cartItems.value.push({
        product_id: String(pId),
        product_name: pName,
        shtrix_code: pShtrix,
        mxik_code: pMxik,
        image_url: pImage,
        brand_name: pBrand,
        quantity: qty,
        price: pPrice,
        unit_name: pUnitName,
        conversion_factor: pConversionFactor
      } as any)
    }

    if (navigator.vibrate) {
      navigator.vibrate(100)
    }

    const uLabel = pUnitName ? ` [${pUnitName}]` : ''
    ElMessage.success(`"${pName}"${uLabel} qo'shildi. Shtrix-kod: ${code}`)
    barcodeInput.value = ''
    quantityInput.value = 1
  } catch (e: any) {
    ElMessage.warning(`Shtrix-kod topilmadi: ${code}`)
    barcodeInput.value = ''
  } finally {
    scanLoading.value = false
  }
}

const removeItem = (index: number) => {
  cartItems.value.splice(index, 1)
}

const totalCartAmount = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.quantity * item.price, 0)
})

// Trigger PC Sale Push
const pcPushLoading = ref(false)
const handlePushPcSale = async () => {
  if (cartItems.value.length === 0) {
    ElMessage.warning('Skanerlangan mahsulotlar mavjud emas!')
    return
  }
  try {
    pcPushLoading.value = true
    const res = (await pushPcSaleApi(
      { pc_user_id: 1, items: cartItems.value },
      deviceToken.value
    )) as any
    if (res && (res.code === 0 || res.push_id)) {
      ElMessage.success('Kompyuter (Kassa) ga muvaffaqiyatli yuborildi!')
      cartItems.value = []
    }
  } catch (err: any) {
    ElMessage.error(err.message || 'Kompyuterga yuborishda xatolik!')
  } finally {
    pcPushLoading.value = false
  }
}

// Mobile Standalone Checkout
const checkoutDialogVisible = ref(false)
const checkoutLoading = ref(false)
const checkoutForm = ref({
  payment_type: 'naqd' as 'naqd' | 'karta' | 'nasiya',
  customer_name: '',
  customer_phone: '',
  paid_amount: 0,
  remark: ''
})

const customerOptions = ref<{ name: string; phone: string }[]>([])

const fetchCustomerOptions = async () => {
  try {
    const res = await getWorkerListApi({ pageIndex: 1, pageSize: 50 })
    if (res && res.data && res.data.list) {
      customerOptions.value = res.data.list.map((w: any) => ({
        name: w.name,
        phone: w.phone || ''
      }))
    }
  } catch (e) {
    // Silent catch
  }
}

const onSelectCustomer = (val: string) => {
  checkoutForm.value.customer_name = val
  const found = customerOptions.value.find((c) => c.name === val)
  if (found && found.phone) {
    checkoutForm.value.customer_phone = found.phone
  }
}

const onPaymentTypeChange = (type: 'naqd' | 'karta' | 'nasiya') => {
  checkoutForm.value.payment_type = type
  if (type === 'nasiya') {
    checkoutForm.value.paid_amount = 0
  } else {
    checkoutForm.value.paid_amount = totalCartAmount.value
  }
}

const remainingDebtAmount = computed(() => {
  return Math.max(0, totalCartAmount.value - (checkoutForm.value.paid_amount || 0))
})

const openCheckout = (paymentType: 'naqd' | 'karta' | 'nasiya' = 'naqd') => {
  if (cartItems.value.length === 0) {
    ElMessage.warning('Skanerlangan mahsulotlar mavjud emas!')
    return
  }
  checkoutForm.value.payment_type = paymentType
  if (paymentType === 'nasiya') {
    checkoutForm.value.paid_amount = 0
  } else {
    checkoutForm.value.paid_amount = totalCartAmount.value
  }
  fetchCustomerOptions()
  checkoutDialogVisible.value = true
}

const handlePhoneCheckout = async () => {
  if (checkoutForm.value.payment_type === 'nasiya' && !checkoutForm.value.customer_name.trim()) {
    ElMessage.warning('Nasiya (Qarz) sotuvi uchun mijoz ismini kiriting!')
    return
  }
  try {
    checkoutLoading.value = true
    const res = (await phoneCheckoutApi(
      {
        payment_type: checkoutForm.value.payment_type,
        items: cartItems.value,
        total_amount: totalCartAmount.value,
        paid_amount: checkoutForm.value.paid_amount,
        customer_name: checkoutForm.value.customer_name,
        customer_phone: checkoutForm.value.customer_phone,
        remark: checkoutForm.value.remark
      },
      deviceToken.value
    )) as any

    if (res && (res.code === 0 || res.receipt_number)) {
      ElMessage.success(
        `Sotuv muvaffaqiyatli! Chek #${res.data?.receipt_number || res.receipt_number}`
      )
      cartItems.value = []
      checkoutDialogVisible.value = false
    }
  } catch (err: any) {
    ElMessage.error(err.message || 'Sotuvni yakunlashda xatolik')
  } finally {
    checkoutLoading.value = false
  }
}

onMounted(() => {
  const queryPairCode = (route.query.pair_code || route.query.token) as string
  if (queryPairCode && queryPairCode.trim()) {
    deviceToken.value = queryPairCode.trim()
    localStorage.setItem('X-Device-Token', deviceToken.value)
    router.replace({ query: {} })
  }

  checkDeviceAuth()
})

onBeforeUnmount(() => {
  stopCameraScanner()
})
</script>

<template>
  <div class="mobile-scanner min-h-screen bg-gray-100 p-10px">
    <!-- Check Auth Screen -->
    <div
      v-if="deviceStatus === 'checking'"
      class="flex justify-center items-center h-80vh text-gray-500"
    >
      Qurilma ulanişi tekshirilmoqda...
    </div>

    <!-- Unpaired Device Screen -->
    <div
      v-else-if="deviceStatus === 'unpaired'"
      class="max-w-400px mx-auto mt-40px bg-white p-20px rounded-lg shadow-md"
    >
      <div
        class="text-20px font-bold text-center text-red-600 mb-10px flex items-center justify-center"
      >
        <Icon icon="ep:circle-close" class="text-red-500 mr-6px text-22px" />
        <span>Qurilma Ulangan Emas</span>
      </div>
      <div class="text-14px text-gray-600 text-center mb-20px">
        Kompyuter ekranidagi QR kodni telefon kamerasi bilan skanerlang yoki ulash kodini kiriting.
      </div>

      <!-- Camera Scanner Container for Auto-Pairing -->
      <div
        v-show="isCameraActive"
        class="relative mb-15px rounded-12px overflow-hidden bg-black border-2 border-blue-500 shadow-xl min-h-240px"
      >
        <div
          id="interactive-viewport"
          class="viewport w-full h-auto min-h-240px max-h-360px bg-black"
        ></div>
        <div
          class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center p-15px"
        >
          <div
            class="relative w-220px h-160px border-2 border-dashed border-emerald-400/80 rounded-12px flex items-center justify-center transition-all duration-300"
            :class="
              scanSuccessFlash
                ? 'bg-emerald-500/40 border-emerald-300 scale-105'
                : 'bg-emerald-500/5'
            "
          >
            <div
              class="absolute left-8px right-8px h-2px bg-emerald-400 shadow-[0_0_10px_#34d399] scan-laser-line"
            ></div>
            <div
              class="absolute -top-2px -left-2px w-18px h-18px border-t-4 border-l-4 border-emerald-400 rounded-tl-6px"
            ></div>
            <div
              class="absolute -top-2px -right-2px w-18px h-18px border-t-4 border-r-4 border-emerald-400 rounded-tr-6px"
            ></div>
            <div
              class="absolute -bottom-2px -left-2px w-18px h-18px border-b-4 border-l-4 border-emerald-400 rounded-bl-6px"
            ></div>
            <div
              class="absolute -bottom-2px -right-2px w-18px h-18px border-b-4 border-r-4 border-emerald-400 rounded-br-6px"
            ></div>
          </div>
          <div
            class="mt-8px text-12px text-white font-semibold bg-black/75 px-12px py-4px rounded-full backdrop-blur-md border border-white/20 inline-flex items-center gap-4px"
          >
            <Icon icon="ep:aim" />
            <span>QR-kodni ushbu ramkaga to'g'rilang</span>
          </div>
        </div>
      </div>

      <ElButton
        :type="isCameraActive ? 'danger' : 'success'"
        class="w-full mb-15px h-45px text-15px font-bold shadow-md inline-flex items-center justify-center"
        @click="toggleCameraScanner"
      >
        <Icon :icon="isCameraActive ? 'ep:close' : 'ep:camera'" class="mr-6px" />
        <span>{{ isCameraActive ? 'Yopish' : 'QR Kod Bilan Ulanish' }}</span>
      </ElButton>

      <ElForm label-position="top">
        <ElFormItem label="Device Token / Ulash kodi">
          <ElInput v-model="pairCodeInput" placeholder="Token yoki ulash kodini kiriting" />
        </ElFormItem>
        <ElButton type="primary" class="w-full" @click="savePairToken"> Ulanish </ElButton>
      </ElForm>
    </div>

    <!-- Paired Device Main Interface -->
    <div v-else class="max-w-500px mx-auto">
      <!-- Device Header -->
      <div
        class="bg-blue-600 text-white p-15px rounded-lg mb-15px flex justify-between items-center shadow-sm"
      >
        <div>
          <div class="text-12px opacity-80">Ulangan Qurilma:</div>
          <div class="text-16px font-bold inline-flex items-center gap-6px">
            <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span>{{ deviceName }}</span>
          </div>
        </div>
        <ElButton size="small" type="warning" plain @click="deviceStatus = 'unpaired'">
          Qayta ulash
        </ElButton>
      </div>

      <!-- Mode Selector -->
      <div class="mb-15px flex justify-center">
        <ElRadioGroup v-model="currentMode" size="large">
          <ElRadioButton label="pc" value="pc">
            <span class="inline-flex items-center gap-4px">
              <Icon icon="ep:monitor" />
              <span>PC Sale (Kompyuterga yuborish)</span>
            </span>
          </ElRadioButton>
          <ElRadioButton label="phone" value="phone">
            <span class="inline-flex items-center gap-4px">
              <Icon icon="ep:cellphone" />
              <span>Phone Sale (Telefondan sotuv)</span>
            </span>
          </ElRadioButton>
        </ElRadioGroup>
      </div>

      <!-- Scanner Input Box & Live Camera Stream -->
      <ElCard class="mb-15px" body-style="padding: 15px;">
        <div class="flex justify-between items-center mb-10px">
          <div class="text-14px font-bold">Skanerlash / Kamera Bilan O'qish</div>
          <div class="flex items-center gap-6px">
            <ElButton
              v-if="isCameraActive && isTorchSupported"
              :type="isTorchActive ? 'warning' : 'info'"
              size="small"
              circle
              @click="toggleTorch"
              title="Chiroq (Flashlight)"
            >
              <Icon icon="ep:opportunity" />
            </ElButton>
            <ElButton
              :type="isCameraActive ? 'danger' : 'primary'"
              size="small"
              plain
              class="inline-flex items-center gap-4px"
              @click="toggleCameraScanner"
            >
              <Icon :icon="isCameraActive ? 'ep:close' : 'ep:camera'" />
              <span>{{ isCameraActive ? 'Yopish' : 'Kamera' }}</span>
            </ElButton>
          </div>
        </div>

        <!-- Live Camera Stream Viewport widget -->
        <div
          v-show="isCameraActive"
          class="relative mb-15px rounded-12px overflow-hidden bg-black border-2 border-blue-500 shadow-xl min-h-240px"
        >
          <div
            id="interactive-viewport"
            class="viewport w-full h-auto min-h-240px max-h-360px bg-black"
          ></div>
          <div
            class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center p-15px"
          >
            <div
              class="relative w-240px h-160px border-2 border-dashed border-emerald-400/80 rounded-12px flex items-center justify-center transition-all duration-300"
              :class="
                scanSuccessFlash
                  ? 'bg-emerald-500/40 border-emerald-300 scale-105'
                  : 'bg-emerald-500/5'
              "
            >
              <div
                class="absolute left-8px right-8px h-2px bg-emerald-400 shadow-[0_0_10px_#34d399] scan-laser-line"
              ></div>
              <div
                class="absolute -top-2px -left-2px w-18px h-18px border-t-4 border-l-4 border-emerald-400 rounded-tl-6px"
              ></div>
              <div
                class="absolute -top-2px -right-2px w-18px h-18px border-t-4 border-r-4 border-emerald-400 rounded-tr-6px"
              ></div>
              <div
                class="absolute -bottom-2px -left-2px w-18px h-18px border-b-4 border-l-4 border-emerald-400 rounded-bl-6px"
              ></div>
              <div
                class="absolute -bottom-2px -right-2px w-18px h-18px border-b-4 border-r-4 border-emerald-400 rounded-br-6px"
              ></div>
            </div>
            <div
              class="mt-8px text-12px text-white font-semibold bg-black/75 px-12px py-4px rounded-full backdrop-blur-md border border-white/20 inline-flex items-center gap-4px"
            >
              <Icon icon="ep:aim" />
              <span>Shtrix-kod yoki QR-kodni ramkaga tuting</span>
            </div>
          </div>
        </div>

        <div
          v-if="lastDetectedBarcode"
          class="mb-10px flex items-center justify-between gap-8px rounded-6px border border-blue-200 bg-blue-50 px-10px py-7px text-12px text-blue-900"
        >
          <span>Oxirgi o'qilgan kod</span>
          <span class="font-mono font-bold break-all text-right">
            {{ lastDetectedBarcode }}
            <span v-if="lastDetectedFormat" class="font-sans font-normal text-blue-600">
              ({{ lastDetectedFormat }})
            </span>
          </span>
        </div>
        <div v-else-if="isCameraActive" class="mb-10px text-center text-12px text-gray-500">
          {{ scannerStatus }}
        </div>

        <div class="flex gap-10px mb-10px">
          <ElInput
            v-model="barcodeInput"
            placeholder="Shtrix-kod yoki QR-kodni kiriting"
            size="large"
            clearable
            @keyup.enter="addScannedItem"
          />
          <ElInput
            v-model.number="quantityInput"
            type="number"
            min="1"
            style="width: 90px"
            size="large"
          />
        </div>
        <ElButton
          type="primary"
          class="w-full"
          size="large"
          :loading="scanLoading"
          @click="addScannedItem"
        >
          + Mahsulot Qo'shish
        </ElButton>
      </ElCard>

      <!-- Cart Items List -->
      <ElCard class="mb-15px" body-style="padding: 15px;">
        <div class="flex justify-between items-center mb-10px">
          <div class="text-14px font-bold">Skanerlangan Mahsulotlar ({{ cartItems.length }})</div>
          <div class="text-18px font-bold text-blue-600">${{ formatMoney(totalCartAmount) }}</div>
        </div>

        <div v-if="cartItems.length === 0" class="text-center py-20px text-gray-400">
          Mahsulotlar skanerlanmagan
        </div>

        <div v-else class="divide-y">
          <div
            v-for="(item, index) in cartItems"
            :key="index"
            class="py-10px flex items-center justify-between gap-10px"
          >
            <div class="flex items-center gap-10px flex-1 overflow-hidden">
              <img
                :src="
                  getProductMainImage(item as any) || getProductFallbackAvatar(item.product_name)
                "
                :alt="item.product_name"
                @error="handleImageError($event, item.product_name)"
                class="w-48px h-48px rounded-8px object-cover border border-gray-200 flex-shrink-0"
              />
              <div class="min-w-0 flex-1">
                <div class="font-bold text-14px text-gray-900 truncate" :title="item.product_name">
                  {{ item.product_name }}
                </div>
                <div class="flex items-center gap-6px mt-2px flex-wrap">
                  <ElTag v-if="(item as any).brand_name" type="success" size="small" effect="light">
                    {{ (item as any).brand_name }}
                  </ElTag>
                  <ElTag
                    v-if="(item as any).unit_name"
                    type="primary"
                    size="small"
                    effect="dark"
                    class="font-mono text-10px"
                  >
                    {{ (item as any).unit_name }}
                  </ElTag>
                  <span class="text-12px text-gray-500 font-mono">Kod: {{ item.shtrix_code }}</span>
                </div>
                <div class="text-12px text-gray-600 font-medium mt-2px">
                  {{ item.quantity }} {{ (item as any).unit_name || 'dona' }} × ${{
                    formatMoney(item.price)
                  }}
                </div>
              </div>
            </div>

            <div class="flex items-center gap-10px">
              <span class="font-bold text-15px text-blue-600"
                >${{ formatMoney(item.price * item.quantity) }}</span
              >
              <ElButton
                type="danger"
                circle
                size="small"
                class="inline-flex items-center justify-center"
                @click="removeItem(index)"
              >
                <Icon icon="ep:delete" />
              </ElButton>
            </div>
          </div>
        </div>
      </ElCard>

      <!-- Action Buttons -->
      <div v-if="currentMode === 'pc'">
        <ElButton
          type="success"
          size="large"
          class="w-full h-50px text-18px font-bold shadow-md inline-flex items-center justify-center gap-6px"
          :loading="pcPushLoading"
          :disabled="cartItems.length === 0"
          @click="handlePushPcSale"
        >
          <Icon icon="ep:position" class="text-20px" />
          <span>Kompyuter (Kassa) ga Yuborish</span>
        </ElButton>
      </div>

      <div v-else class="grid grid-cols-3 gap-10px">
        <ElButton
          type="success"
          size="large"
          class="h-50px text-15px font-bold shadow-md !ml-0 inline-flex items-center justify-center gap-4px"
          :disabled="cartItems.length === 0"
          @click="openCheckout('naqd')"
        >
          <Icon icon="ep:money" />
          <span>Naqd</span>
        </ElButton>
        <ElButton
          type="primary"
          size="large"
          class="h-50px text-15px font-bold shadow-md !ml-0 inline-flex items-center justify-center gap-4px"
          :disabled="cartItems.length === 0"
          @click="openCheckout('karta')"
        >
          <Icon icon="ep:credit-card" />
          <span>Karta</span>
        </ElButton>
        <ElButton
          type="warning"
          size="large"
          class="h-50px text-15px font-bold shadow-md !ml-0 inline-flex items-center justify-center gap-4px"
          :disabled="cartItems.length === 0"
          @click="openCheckout('nasiya')"
        >
          <Icon icon="ep:document" />
          <span>{{ t('erp.debt') }}</span>
        </ElButton>
      </div>
    </div>

    <!-- Phone POS Checkout Dialog -->
    <ElDialog
      v-model="checkoutDialogVisible"
      title="Telefondan Sotuv Kassasi (POS)"
      width="450px"
      append-to-body
    >
      <ElForm label-position="top">
        <ElFormItem label="To'lov Usulini Tanlang">
          <ElRadioGroup
            v-model="checkoutForm.payment_type"
            size="large"
            class="w-full flex justify-between"
            @change="onPaymentTypeChange"
          >
            <ElRadioButton label="naqd" value="naqd">
              <span class="inline-flex items-center gap-4px">
                <Icon icon="ep:money" />
                <span>Naqd</span>
              </span>
            </ElRadioButton>
            <ElRadioButton label="karta" value="karta">
              <span class="inline-flex items-center gap-4px">
                <Icon icon="ep:credit-card" />
                <span>Karta</span>
              </span>
            </ElRadioButton>
            <ElRadioButton label="nasiya" value="nasiya">
              <span class="inline-flex items-center gap-4px">
                <Icon icon="ep:document" />
                <span>{{ t('erp.debt') }}</span>
              </span>
            </ElRadioButton>
          </ElRadioGroup>
        </ElFormItem>

        <div class="bg-gray-50 border p-12px rounded-lg mb-15px">
          <div class="flex justify-between items-center mb-5px text-14px font-medium">
            <span>Jami Sotuv Summasi:</span>
            <span class="text-16px font-bold text-blue-600"
              >${{ formatMoney(totalCartAmount) }}</span
            >
          </div>

          <div
            v-if="checkoutForm.payment_type === 'nasiya'"
            class="flex justify-between items-center text-14px font-medium text-amber-600"
          >
            <span>To'lanadigan (Boshlang'ich) Summa:</span>
            <div class="w-130px">
              <ElInput
                v-model.number="checkoutForm.paid_amount"
                type="number"
                min="0"
                :max="totalCartAmount"
                size="small"
              />
            </div>
          </div>

          <div
            v-if="checkoutForm.payment_type === 'nasiya'"
            class="flex justify-between items-center mt-5px text-14px font-bold text-red-600"
          >
            <span>Qolgan Nasiya (Qarz) Summasi:</span>
            <span class="text-16px">${{ formatMoney(remainingDebtAmount) }}</span>
          </div>
        </div>

        <ElFormItem label="Mijoz / Qarzdor Ismi">
          <ElSelect
            v-model="checkoutForm.customer_name"
            placeholder="Mijozni tanlang yoki yangi ism kiriting..."
            filterable
            allow-create
            default-first-option
            class="w-full"
            @change="onSelectCustomer"
          >
            <ElOption
              v-for="c in customerOptions"
              :key="c.name"
              :label="c.name + (c.phone ? ' (' + c.phone + ')' : '')"
              :value="c.name"
            />
          </ElSelect>
        </ElFormItem>

        <ElFormItem label="Mijoz Telefon Raqami">
          <ElInput v-model="checkoutForm.customer_phone" placeholder="+998 90 123 45 67" />
        </ElFormItem>

        <ElFormItem label="Izoh / Qayd">
          <ElInput v-model="checkoutForm.remark" placeholder="Sotuv yoki qarz haqida izoh..." />
        </ElFormItem>
      </ElForm>

      <template #footer>
        <ElButton @click="checkoutDialogVisible = false">{{ t('common.cancel') }}</ElButton>
        <ElButton type="success" :loading="checkoutLoading" @click="handlePhoneCheckout">
          Tasdiqlash & Sotish
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.mobile-scanner {
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
}

:deep(#interactive-viewport video) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

:deep(#interactive-viewport canvas) {
  display: none !important;
}

@keyframes laserSweep {
  0% {
    top: 10px;
    opacity: 0.7;
  }
  50% {
    top: 140px;
    opacity: 1;
  }
  100% {
    top: 10px;
    opacity: 0.7;
  }
}

.scan-laser-line {
  animation: laserSweep 2.2s ease-in-out infinite;
}
</style>
