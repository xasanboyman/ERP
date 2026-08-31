import { getAIConfigApi } from '@/api/ai'
import { dispatchAIFunction } from './aiDispatcher'
import { useUserStore } from '@/store/modules/user'

const WORKLET_CODE = `
class PCMProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0];
    if (input && input[0] && input[0].length > 0) {
      const channelData = input[0];
      const pcmData = new Int16Array(channelData.length);
      for (let i = 0; i < channelData.length; i++) {
        const sample = Math.max(-1, Math.min(1, channelData[i]));
        pcmData[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
      }
      this.port.postMessage(pcmData);
    }
    return true;
  }
}
registerProcessor('pcm-processor', PCMProcessor);
`

const PERMISSION_MAP: Record<string, { resource: string; action: string }> = {
  create_worker: { resource: 'hr.sotrudniki', action: 'create' },
  update_worker: { resource: 'hr.sotrudniki', action: 'update' },
  delete_worker: { resource: 'hr.sotrudniki', action: 'delete' },
  list_workers: { resource: 'hr.sotrudniki', action: 'view' },

  create_product: { resource: 'products.spisok_tovarov', action: 'create' },
  add_product_stock: { resource: 'products.spisok_tovarov', action: 'create' },
  update_product: { resource: 'products.spisok_tovarov', action: 'update' },
  delete_product: { resource: 'products.spisok_tovarov', action: 'delete' },
  list_products: { resource: 'products.spisok_tovarov', action: 'view' },
  search_product: { resource: 'products.spisok_tovarov', action: 'view' },

  create_department: { resource: 'hr.otdel', action: 'create' },
  list_departments: { resource: 'hr.otdel', action: 'view' },

  create_position: { resource: 'hr.dolzhnosti', action: 'create' },
  list_positions: { resource: 'hr.dolzhnosti', action: 'view' },

  create_timesheet: { resource: 'hr.tabel', action: 'create' },

  create_staff_output: { resource: 'hr.vyrabotka', action: 'create' },
  list_staff_outputs: { resource: 'hr.vyrabotka', action: 'view' },

  create_staff_adjustment: { resource: 'hr.korrektirovki', action: 'create' },
  list_staff_adjustments: { resource: 'hr.korrektirovki', action: 'view' },

  list_users: { resource: 'staff.users', action: 'view' },

  list_sales: { resource: 'sales.istoriya_prodazh', action: 'view' },
  get_sale_receipt: { resource: 'sales.istoriya_prodazh', action: 'view' },
  list_debtors: { resource: 'sales.istoriya_prodazh', action: 'view' },
  repay_debt: { resource: 'sales.istoriya_prodazh', action: 'create' },

  list_salaries: { resource: 'hr.vedomost', action: 'view' },
  create_salary: { resource: 'hr.vedomost', action: 'create' },
  salary_payout: { resource: 'hr.vedomost', action: 'create' },

  list_roles: { resource: 'staff.roles', action: 'view' },
  create_role: { resource: 'staff.roles', action: 'create' },
  delete_role: { resource: 'staff.roles', action: 'delete' },

  list_branches: { resource: 'products.spisok_tovarov', action: 'view' },
  create_branch: { resource: 'products.spisok_tovarov', action: 'create' },

  create_cutting_order: { resource: 'cutting.raskroi', action: 'create' },
  delete_cutting_order: { resource: 'cutting.raskroi', action: 'delete' },
  list_cutting_orders: { resource: 'cutting.raskroi', action: 'view' },
  start_production: { resource: 'cutting.raskroi', action: 'update' },
  list_cutting_tasks: { resource: 'cutting.raskroi', action: 'view' },
  update_task_status: { resource: 'cutting.raskroi', action: 'update' },

  generate_qr_code: { resource: 'qr_codes.print', action: 'create' },
  list_qr_codes: { resource: 'qr_codes.print', action: 'view' },
  delete_qr_code: { resource: 'qr_codes.print', action: 'delete' }
}

class AudioQueue {
  private nextPlayTime: number = 0
  private audioCtx: AudioContext
  private analyser: AnalyserNode
  private activeSources: Set<AudioBufferSourceNode> = new Set()

  constructor(audioCtx: AudioContext, analyser: AnalyserNode) {
    this.audioCtx = audioCtx
    this.analyser = analyser
  }

  playChunk(int16Array: Int16Array) {
    const buffer = this.audioCtx.createBuffer(1, int16Array.length, 24000)
    const channelData = buffer.getChannelData(0)
    for (let i = 0; i < int16Array.length; i++) {
      channelData[i] = int16Array[i] / 32768.0
    }

    const source = this.audioCtx.createBufferSource()
    source.buffer = buffer
    source.connect(this.analyser)
    this.analyser.connect(this.audioCtx.destination)

    const now = this.audioCtx.currentTime
    if (this.nextPlayTime < now) {
      this.nextPlayTime = now
    }
    source.start(this.nextPlayTime)
    this.nextPlayTime += buffer.duration

    this.activeSources.add(source)
    source.onended = () => {
      this.activeSources.delete(source)
    }
  }

  stopAll() {
    for (const s of this.activeSources) {
      try {
        s.stop()
        s.disconnect()
      } catch {}
    }
    this.activeSources.clear()
    this.nextPlayTime = 0
  }

  isPlaying(): boolean {
    return this.activeSources.size > 0 && this.nextPlayTime > this.audioCtx.currentTime
  }

  clear() {
    this.stopAll()
  }
}

export class AIVoiceClient {
  private apiKey: string = ''
  private ws: WebSocket | null = null
  private audioContext: AudioContext | null = null
  private playbackAudioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private workletNode: AudioWorkletNode | null = null
  private mediaSourceNode: MediaStreamAudioSourceNode | null = null
  private consecutiveVoiceFrames: number = 0

  public isConnected: boolean = false
  public isConnecting: boolean = false
  public isUserSpeaking: boolean = false

  private systemInstruction: string = ''
  private permissions: Record<string, string[]> = {}
  private allowedTools: string[] = []
  private isSuper: boolean = false
  private currentUsername: string = ''
  private currentUserRole: string = ''
  private audioQueue: AudioQueue | null = null
  private micAnalyser: AnalyserNode | null = null
  private playbackAnalyser: AnalyserNode | null = null

  // Callbacks
  public onStatusChange: ((status: 'disconnected' | 'connecting' | 'connected') => void) | null =
    null
  public onTranscription:
    ((role: 'user' | 'model', text: string, isFinal: boolean) => void) | null = null
  public onAudioLevel: ((level: number) => void) | null = null
  public onFrequencyData:
    | ((data: {
        raw: Uint8Array
        bass: number
        mid: number
        high: number
        level: number
        source: 'playback' | 'mic' | 'idle'
      }) => void)
    | null = null
  public onToolExecution:
    ((info: { action: string; requests: string[]; message: string; data?: any }) => void) | null =
    null

  async init() {
    try {
      const userStore = useUserStore()
      this.currentUsername = userStore.getUserInfo?.username || ''
      const res = await getAIConfigApi(this.currentUsername)
      if (res && res.code === 0) {
        this.apiKey = res.data.gemini_api_key
        this.permissions = res.data.permissions || {}
        this.allowedTools = res.data.allowed_tools || []
        this.isSuper = res.data.user?.is_super || false
        this.currentUserRole = res.data.user?.role || 'User'
        this.systemInstruction = this.buildInstruction(res.data)
      }
    } catch (err) {
      console.error('Failed to load AI configuration:', err)
    }
  }

  private buildInstruction(data: any): string {
    const isSuperAdmin = data.user?.is_super || false
    const roleName = data.user?.role || 'Foydalanuvchi'
    const userName = data.user?.name || 'Foydalanuvchi'
    const allowed = this.allowedTools || []

    let roleSection = ''
    if (isSuperAdmin) {
      roleSection = `Siz to'liq administratorlik huquqiga egasiz (Super Admin).
Siz Model Context Protocol (MCP) orqali ERP tizimidagi barcha modullarni: omborxona, mahsulotlar, savdolar, nasiyalar, HR/xodimlar, oyliklar, ishlab chiqarish (raskroy), QR kodlar va tahlillarni to'liq boshqara olasiz.`
    } else {
      const toolsListStr = allowed.join(', ')
      roleSection = `FOYDALANUVCHI VAKOLATI VA HUQUQI (MCP RBAC):
Foydalanuvchi: ${userName} | Rol: ${roleName}.
Sizga ushbu foydalanuvchi uchun FAQAT quyidagi ruxsat berilgan MCP funksiyalari biriktirilgan: [${toolsListStr}].

XAVFSIZLIK VA MA'LUMOT SIR SAQLASH QOIDALARI:
1. Siz FAQAT foydalanuvchiga ruxsat etilgan MCP function declarations (tools) orqali ma'lumot olasiz va amallarni bajarasiz.
2. Ruxsat berilmagan ma'lumotlar (masalan: boshqa xodimlar maoshlari, shaxsiy ma'lumotlar yoki tizim sozlamalari) haqida hech qanday ma'lumot bermang.
3. Agar foydalanuvchi o'z vakolatidan tashqari amalni so'rasa, xushmuomalalik bilan:
   "Kechirasiz, sizning hisobingizda bu amalni bajarish yoki ushbu ma'lumotni ko'rish uchun ruxsat yo'q." deb javob bering.`
    }

    return `Siz Knit ERP (Antigravity AI) tizimining Model Context Protocol (MCP) bilan to'liq integratsiyalashgan aqlli, xavfsiz va tezkor ovozli/matnli yordamchisisiz.

${roleSection}

MODEL CONTEXT PROTOCOL (MCP) ISHLASH PRINSIPLARI:
1. MCP TOOL-FIRST STRATEGIYASI:
   - Foydalanuvchi buyruq yoki savol berganda, HECH QACHON tool call bajarishdan oldin gapirmang yoki taxmin qilmang.
   - Avval kerakli MCP toolni (funksiyani) aniq parametrlar bilan chaqiring.
   - Tool natijasi kelgandan so'ng, faqat qaytgan haqiqiy ma'lumotlarga asoslanib qisqa, aniq va lo'nda javob bering.

2. ASOSIY MODULLAR BO'YICHA MCP FUNKSIYALARI:
   - OMBOR & MAHSULOTLAR (SMART INVENTORY RESOLUTION):
     * Mahsulot kiritish / zaxira qo'shish (masalan: "Coca Cola 1.5L dan 20 ta keldik", "Pepsi 10 ta qo'sh"):
       -> FAQAT 'add_product_stock' funksiyasini chaqiring.
       -> MAJBURIY PARAMETR: 'name' (va 'added_quantity', aytilmagan bo'lsa 1).
       -> IXTIYORIY PARAMETRLAR: 'price', 'cost', 'brand_name', 'expiration_date'. Foydalanuvchi narx yoki muddat aytmasa ham, to'xtamasdan 'add_product_stock'ni chaqiring!
       -> ISHLASH TIZIMI: Tizim avval ombordan qidiradi, agar topilmasa 411,000+ Milliy Mahsulot Klassifikatoridan (MXIK va Brend) avtomatik topib yangi mahsulot yaratadi va zaxirasini to'ldiradi.
     * Mahsulot qoldig'i yoki narxini tekshirish: 'list_products' (search parametriga AYNAN mahsulot nomini yozing).
     * Kam qolgan tovarlar: 'get_low_stock_products'.
   - SAVDO, KASSA & NASIYA (DEBTORS):
     * So'nggi savdolar: 'list_sales', 'get_sale_receipt'.
     * Qarzdorlar ro'yxati: 'list_debtors'.
     * Qarzni so'ndirish / to'lov qabul qilish: 'repay_debt'.
   - HR & XODIMLAR:
     * Xodim qo'shish / ro'yxati: 'create_worker', 'list_workers', 'update_worker'.
     * Bo'limlar va lavozimlar: 'list_departments', 'create_department', 'list_positions', 'create_position'.
     * Oylik maoshlar & Vedomost: 'list_salaries', 'create_salary'.
     * Ishbay hajm & Qo'shimchalar: 'create_staff_output', 'create_staff_adjustment'.
   - ISHLAB CHIQARISH (RASKROY):
     * Kesish buyurtmalari: 'list_cutting_orders', 'create_cutting_order', 'start_production'.
     * Jarayonlar va vazifalar: 'get_task_list', 'update_task_status'.

3. MULOQOT STANDARTI:
   - Foydalanuvchi bilan FAQAT o'zbek tilida muloqot qiling.
   - Javoblaringiz professional, aniq, faktlarga asoslangan va keraksiz so'zlarsiz bo'lsin.`
  }

  async connect() {
    if (this.isConnected || this.isConnecting) return
    if (!this.apiKey) {
      await this.init()
    }
    if (!this.apiKey) {
      alert('Gemini API key is not configured in backend .env file!')
      return
    }

    this.isConnecting = true
    this.updateStatus('connecting')

    const url = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${this.apiKey}`

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        this.isConnected = true
        this.isConnecting = false
        this.updateStatus('connected')
        this.sendSetup()
        this.startMic()
      }

      this.ws.onmessage = async (event) => {
        try {
          let data = event.data
          if (data instanceof Blob) {
            data = await data.text()
          }
          if (typeof data === 'string') {
            const msg = JSON.parse(data)
            this.handleServerMessage(msg)
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
        }
      }

      this.ws.onclose = (event) => {
        console.warn(
          `[AI] WebSocket closed — code: ${event.code}, reason: "${event.reason || 'none'}"`
        )
        this.disconnect()
      }

      this.ws.onerror = (err) => {
        console.error('[AI] WebSocket Error:', err)
        this.disconnect()
      }
    } catch (err) {
      console.error('Connection failed:', err)
      this.disconnect()
    }
  }

  disconnect() {
    this.isConnected = false
    this.isConnecting = false
    this.updateStatus('disconnected')

    if (this.ws) {
      try {
        this.ws.close()
      } catch (e) {
        console.debug(e)
      }
      this.ws = null
    }

    this.stopMic()

    if (this.audioContext) {
      try {
        this.audioContext.close()
      } catch (e) {
        console.debug(e)
      }
      this.audioContext = null
    }
    if (this.playbackAudioContext) {
      try {
        this.playbackAudioContext.close()
      } catch (e) {
        console.debug(e)
      }
      this.playbackAudioContext = null
    }
    this.audioQueue = null
  }

  private updateStatus(status: 'disconnected' | 'connecting' | 'connected') {
    if (this.onStatusChange) this.onStatusChange(status)
  }

  private sendSetup() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return

    const setupMsg = {
      setup: {
        model: 'models/gemini-3.1-flash-live-preview',
        generationConfig: {
          responseModalities: ['AUDIO'],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: {
                voiceName: 'Puck'
              }
            }
          },
          thinkingConfig: {
            thinkingLevel: 'MINIMAL'
          }
        },
        systemInstruction: {
          parts: [{ text: this.systemInstruction }]
        },
        tools: [{ functionDeclarations: this.getDeclarations() }]
      }
    }

    this.ws.send(JSON.stringify(setupMsg))
  }

  private getDeclarations() {
    const allDeclarations = [
      {
        name: 'create_worker',
        description: "Yangi xodim qo'shish / yaratish. Telefon raqami majburiy.",
        parameters: {
          type: 'OBJECT',
          properties: {
            first_name: { type: 'STRING', description: 'Xodim ismi.' },
            last_name: { type: 'STRING', description: 'Xodim familiyasi.' },
            position: { type: 'STRING', description: 'Lavozim nomi.' },
            department: { type: 'STRING', description: "Bo'lim nomi." },
            phone: { type: 'STRING', description: 'Telefon raqami (masalan, +998901234567).' },
            salary: { type: 'NUMBER', description: 'Ish haqi miqdori.' }
          },
          required: ['first_name', 'last_name', 'phone']
        }
      },
      {
        name: 'update_worker',
        description: "Mavjud xodim ma'lumotlarini yangilash/tahrirlash.",
        parameters: {
          type: 'OBJECT',
          properties: {
            worker_id: { type: 'STRING', description: 'Xodim IDsi.' },
            first_name: { type: 'STRING', description: 'Xodim yangi ismi.' },
            last_name: { type: 'STRING', description: 'Xodim yangi familiyasi.' },
            position: { type: 'STRING', description: 'Yangi lavozim.' },
            phone: { type: 'STRING', description: 'Yangi telefon raqami.' },
            salary: { type: 'NUMBER', description: 'Yangi ish haqi miqdori.' }
          },
          required: ['worker_id']
        }
      },
      {
        name: 'delete_worker',
        description: "Xodimni tizimdan o'chirish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            worker_id: { type: 'STRING', description: "O'chirilishi kerak bo'lgan xodim IDsi." }
          },
          required: ['worker_id']
        }
      },
      {
        name: 'list_workers',
        description: "Tizimdagi barcha xodimlar ro'yxatini olish."
      },
      {
        name: 'add_product_stock',
        description:
          "Ombordagi mahsulot zaxirasini oshirish yoki yangi mahsulot kirim qilish. Agar mahsulot omborda yo'q bo'lsa, tizim avtomatik 411,000+ Milliy klassifikatordan MXIK kodi va brend ma'lumotlarini topib omborga yangi mahsulot sifatida kiritadi.",
        parameters: {
          type: 'OBJECT',
          properties: {
            name: {
              type: 'STRING',
              description: 'Mahsulot nomi (MAJBURIY). Masalan: Coca Cola 1.5l, Pepsi 0.5l, Fanta.'
            },
            added_quantity: {
              type: 'NUMBER',
              description: "Qo'shilayotgan dona soni (ixtiyoriy, default 1)."
            },
            price: { type: 'NUMBER', description: 'Sotuv narxi (ixtiyoriy).' },
            cost: { type: 'NUMBER', description: 'Tannarxi / kelish narxi (ixtiyoriy).' },
            brand_name: {
              type: 'STRING',
              description: 'Brend nomi (masalan: COCA-COLA, PEPSI - ixtiyoriy).'
            },
            expiration_date: {
              type: 'STRING',
              description: 'Yaroqlilik muddati YYYY-MM-DD formatida (ixtiyoriy).'
            }
          },
          required: ['name']
        }
      },
      {
        name: 'create_product',
        description:
          'Yangi mahsulot yaratish (faqat foydalanuvchi aniq "yangi mahsulot yarat" deganda).',
        parameters: {
          type: 'OBJECT',
          properties: {
            name: { type: 'STRING', description: 'Mahsulot nomi.' },
            quantity: { type: 'NUMBER', description: "Boshlang'ich miqdor." },
            price: { type: 'NUMBER', description: 'Sotuv narxi.' },
            cost: { type: 'NUMBER', description: 'Tannarxi.' },
            brand_name: { type: 'STRING', description: 'Brend nomi.' },
            expiration_date: { type: 'STRING', description: 'Yaroqlilik muddati YYYY-MM-DD.' }
          },
          required: ['name']
        }
      },
      {
        name: 'update_product',
        description: "Mavjud mahsulot ma'lumotlarini yangilash/tahrirlash.",
        parameters: {
          type: 'OBJECT',
          properties: {
            product_id: { type: 'STRING', description: 'Mahsulot IDsi.' },
            name: { type: 'STRING', description: 'Yangi nomi.' },
            price: { type: 'NUMBER', description: 'Yangi sotuv narxi.' },
            quantity: { type: 'NUMBER', description: 'Ombordagi yangi miqdori.' },
            expiration_date: { type: 'STRING', description: 'Yaroqlilik muddati (YYYY-MM-DD).' }
          },
          required: ['product_id']
        }
      },
      {
        name: 'delete_product',
        description: "Mahsulotni tizimdan o'chirish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            product_id: { type: 'STRING', description: "O'chiriladigan mahsulot IDsi." }
          },
          required: ['product_id']
        }
      },
      {
        name: 'list_products',
        description:
          "Omborimizda mavjud mahsulotlarni qidirish yoki ro'yxatini ko'rish. search parametriga foydalanuvchi aytgan mahsulot nomini AYNAN yozing.",
        parameters: {
          type: 'OBJECT',
          properties: {
            search: {
              type: 'STRING',
              description:
                "Mahsulot nomi. Foydalanuvchi aytgan aynan so'z. Masalan: Fanta, Pepsi 1.5l, Sheker."
            }
          }
        }
      },
      {
        name: 'create_department',
        description: "Yangi bo'lim yaratish/qo'shish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            name: { type: 'STRING', description: "Bo'lim nomi." },
            description: { type: 'STRING', description: 'Tavsif/Remark.' }
          },
          required: ['name']
        }
      },
      {
        name: 'list_departments',
        description: "Bo'limlar ro'yxatini olish."
      },
      {
        name: 'create_position',
        description: 'Yangi lavozim yaratish.',
        parameters: {
          type: 'OBJECT',
          properties: {
            name: { type: 'STRING', description: 'Lavozim nomi.' },
            salary: { type: 'NUMBER', description: 'Baza ish haqi.' },
            description: { type: 'STRING', description: 'Tavsif/Remark.' }
          },
          required: ['name', 'salary']
        }
      },
      {
        name: 'list_positions',
        description: "Lavozimlar ro'yxatini olish."
      },
      {
        name: 'create_timesheet',
        description: 'Yangi davomat (timesheet) varaqasini yaratish.',
        parameters: {
          type: 'OBJECT',
          properties: {
            date: { type: 'STRING', description: 'Davomat sanasi (YYYY-MM-DD).' },
            records: {
              type: 'ARRAY',
              description: 'Xodimlar davomati yozuvlari.',
              items: {
                type: 'OBJECT',
                properties: {
                  workerId: { type: 'STRING', description: 'Xodim IDsi.' },
                  status: { type: 'STRING', description: 'Holati (present/absent/late).' }
                },
                required: ['workerId', 'status']
              }
            }
          }
        }
      },
      {
        name: 'create_staff_output',
        description: 'Xodimning bajargan ish hajmini (ishbay oylik uchun) kiritish.',
        parameters: {
          type: 'OBJECT',
          properties: {
            worker_id: { type: 'STRING', description: 'Xodim IDsi.' },
            name: { type: 'STRING', description: 'Ish/operatsiya nomi.' },
            amount: { type: 'NUMBER', description: 'Ish hajmi miqdori.' },
            period_month: { type: 'STRING', description: 'Oylik davr (YYYY-MM).' },
            comment: { type: 'STRING', description: 'Izoh.' }
          },
          required: ['worker_id', 'amount']
        }
      },
      {
        name: 'create_staff_adjustment',
        description: "Xodim uchun qo'shimcha to'lovlar (bonus, jarima, avans) yozish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            worker_id: { type: 'STRING', description: 'Xodim IDsi.' },
            document_type: {
              type: 'STRING',
              description: 'Hujjat turi (bonus, penalty, advance).'
            },
            amount: { type: 'NUMBER', description: 'Miqdori.' },
            period_month: { type: 'STRING', description: 'Oylik davr (YYYY-MM).' },
            description: { type: 'STRING', description: 'Tavsif/Sababi.' }
          },
          required: ['worker_id', 'document_type', 'amount']
        }
      },
      {
        name: 'list_staff_outputs',
        description: "Ishbay bajarilgan ishlar ro'yxatini olish."
      },
      {
        name: 'list_staff_adjustments',
        description: "Xodimlar to'lovlarini (bonuslar, jarimalar) olish."
      },
      {
        name: 'list_users',
        description: "Tizim foydalanuvchilari ro'yxatini olish."
      },
      {
        name: 'create_role',
        description: "Yangi rol yaratish/qo'shish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            name: { type: 'STRING', description: 'Rol nomi.' },
            remark: { type: 'STRING', description: 'Tavsif/Izoh.' },
            permissions: {
              type: 'ARRAY',
              description: "Rol huquqlari ro'yxati.",
              items: { type: 'STRING' }
            }
          },
          required: ['name']
        }
      },
      {
        name: 'delete_role',
        description: "Mavjud rolni tizimdan o'chirish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            role_id: { type: 'STRING', description: "O'chirilishi kerak bo'lgan rol IDsi." }
          },
          required: ['role_id']
        }
      },
      {
        name: 'list_roles',
        description: "Tizimdagi barcha rollar ro'yxatini olish."
      },

      // --- SALES ---
      {
        name: 'list_sales',
        description: "So'nggi sotuvlar tarixini ko'rish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            search: { type: 'STRING', description: 'Qidiruv (mijoz ismi, chek raqami).' },
            payment_method: { type: 'STRING', description: "To'lov turi (naqd/karta/nasiya)." },
            limit: { type: 'NUMBER', description: 'Nechta yozuv (default 20).' }
          }
        }
      },
      {
        name: 'get_sale_receipt',
        description: 'Sotish chekini (kvitansiyasini) olish.',
        parameters: {
          type: 'OBJECT',
          properties: {
            receipt_number: { type: 'STRING', description: 'Chek raqami.' }
          },
          required: ['receipt_number']
        }
      },
      {
        name: 'list_debtors',
        description: "Nasiya/qarz mijozlar ro'yxatini olish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            search: { type: 'STRING', description: 'Mijoz ismi yoki telefoni.' }
          }
        }
      },
      {
        name: 'repay_debt',
        description: "Mijozning qarzini to'lashtirish/qaytarish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            customer_name: { type: 'STRING', description: 'Mijoz ismi.' },
            customer_phone: { type: 'STRING', description: 'Mijoz telefoni.' },
            amount: { type: 'NUMBER', description: "To'lov miqdori." },
            payment_method: { type: 'STRING', description: "To'lov turi (naqd/karta)." },
            remark: { type: 'STRING', description: 'Izoh.' }
          },
          required: ['customer_name', 'amount']
        }
      },

      // --- BRANCHES ---
      {
        name: 'list_branches',
        description: "Filiallar ro'yxatini olish."
      },
      {
        name: 'create_branch',
        description: 'Yangi filial yaratish.',
        parameters: {
          type: 'OBJECT',
          properties: {
            name: { type: 'STRING', description: 'Filial nomi.' },
            address: { type: 'STRING', description: 'Manzil.' },
            phone: { type: 'STRING', description: 'Telefon raqami.' },
            code: { type: 'STRING', description: 'Filial kodi.' }
          },
          required: ['name']
        }
      },

      // --- ANALYTICS & REPORTS ---
      {
        name: 'get_top_selling_products',
        description: "Eng ko'p sotilgan tovarlar va mahsulotlar reytingi (top selling products), har bir tovarning sotilgan dona soni va umumiy tushumi."
      },
      {
        name: 'get_sales_analytics',
        description: "Umumiy sotuvlar soni, kassa tushumi va to'lov usullari bo'yicha to'liq statistika."
      },
      {
        name: 'get_debt_report',
        description: "Mijozlarning jami qarzlari, faol qarzdorlar va nasiyalar hisoboti."
      },

      // --- SALARY ---
      {
        name: 'list_salaries',
        description: "Ish haqi ro'yxatini olish.",
        parameters: {
          type: 'OBJECT',
          properties: {
            worker_id: { type: 'STRING', description: 'Xodim IDsi (ixtiyoriy).' }
          }
        }
      },
      {
        name: 'salary_payout',
        description: "Xodimlar(ga) oylik to'lash.",
        parameters: {
          type: 'OBJECT',
          properties: {
            worker_ids: {
              type: 'ARRAY',
              description: "Xodimlar IDlari ro'yxati.",
              items: { type: 'STRING' }
            },
            allowance: { type: 'NUMBER', description: "Qo'shimcha to'lov miqdori." },
            deduction: { type: 'NUMBER', description: 'Ushlab qolish miqdori.' },
            remark: { type: 'STRING', description: 'Izoh.' }
          },
          required: ['worker_ids']
        }
      }
    ]

    return allDeclarations.filter((decl) => {
      if (this.isSuper) return true
      if (this.allowedTools && this.allowedTools.length > 0) {
        return this.allowedTools.includes(decl.name)
      }
      const req = PERMISSION_MAP[decl.name]
      if (!req) return false
      const allowedActions = this.permissions[req.resource]
      return allowedActions && (allowedActions.includes(req.action) || allowedActions.includes('*'))
    })
  }

  private async startMic() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })

      this.audioContext = new AudioContext({ sampleRate: 16000 })
      this.micAnalyser = this.audioContext.createAnalyser()
      this.micAnalyser.fftSize = 256
      this.micAnalyser.smoothingTimeConstant = 0.8

      this.mediaSourceNode = this.audioContext.createMediaStreamSource(this.mediaStream)
      this.mediaSourceNode.connect(this.micAnalyser)

      // Initialize playback context early
      this.playbackAudioContext = new AudioContext({ sampleRate: 24000 })
      this.playbackAnalyser = this.playbackAudioContext.createAnalyser()
      this.playbackAnalyser.fftSize = 256
      this.playbackAnalyser.smoothingTimeConstant = 0.85
      this.audioQueue = new AudioQueue(this.playbackAudioContext, this.playbackAnalyser)

      // Track sustained human speech for 1.0s - 1.5s barge-in
      let speechStartTimestamp = 0
      let silenceStartTimestamp = 0

      // Multi-band frequency data buffers
      const micDataArray = new Uint8Array(this.micAnalyser.frequencyBinCount)
      const playbackDataArray = new Uint8Array(this.playbackAnalyser.frequencyBinCount)

      const checkAudioLevel = () => {
        if (!this.isConnected) return

        let activeSource: 'playback' | 'mic' | 'idle' = 'idle'
        let targetData = micDataArray

        const isModelPlaying = this.audioQueue?.isPlaying() || false

        if (isModelPlaying && this.playbackAnalyser) {
          this.playbackAnalyser.getByteFrequencyData(playbackDataArray)
          targetData = playbackDataArray
          activeSource = 'playback'
        } else if (this.micAnalyser) {
          this.micAnalyser.getByteFrequencyData(micDataArray)
          targetData = micDataArray
          activeSource = 'mic'
        }

        // Multi-band frequency breakdown (Bass: 0-8, Mid/Voice: 8-45, High: 45-128)
        let bassSum = 0,
          midSum = 0,
          highSum = 0,
          totalSum = 0
        const totalBins = targetData.length
        const bassCount = Math.min(10, totalBins)
        const midCount = Math.min(50, totalBins - bassCount)
        const highCount = Math.max(1, totalBins - bassCount - midCount)

        for (let i = 0; i < totalBins; i++) {
          const val = targetData[i]
          totalSum += val
          if (i < bassCount) {
            bassSum += val
          } else if (i < bassCount + midCount) {
            midSum += val
          } else {
            highSum += val
          }
        }

        const avg = totalSum / totalBins
        const bassLevel = bassSum / Math.max(1, bassCount)
        const midLevel = midSum / Math.max(1, midCount)
        const highLevel = highSum / Math.max(1, highCount)

        if (this.onAudioLevel) this.onAudioLevel(avg)

        if (this.onFrequencyData) {
          this.onFrequencyData({
            raw: targetData,
            bass: bassLevel,
            mid: midLevel,
            high: highLevel,
            level: avg,
            source: avg > 6 ? activeSource : 'idle'
          })
        }

        // BARGE-IN SPEAKING CANCELLATION (Continuous Human Speech for 1.0s - 1.5s):
        // Focus specifically on the human speech vocal formant band (bins 8 to 45: ~250Hz - 3500Hz)
        if (this.micAnalyser && isModelPlaying) {
          this.micAnalyser.getByteFrequencyData(micDataArray)
          let userVocalSum = 0
          for (let i = 8; i < 48 && i < micDataArray.length; i++) {
            userVocalSum += micDataArray[i]
          }
          const userVocalEnergy = userVocalSum / 40
          const now = Date.now()

          // Human speech vocal band threshold (ignores brief ambient clicks/taps)
          if (userVocalEnergy >= 30) {
            silenceStartTimestamp = 0
            if (speechStartTimestamp === 0) {
              speechStartTimestamp = now
            } else {
              const speechDuration = now - speechStartTimestamp
              // Only cancel AI speech once user has been continuously speaking words for >= 1.2s (1s-1.5s)
              if (speechDuration >= 1200) {
                this.audioQueue?.stopAll()
                speechStartTimestamp = 0
              }
            }
          } else {
            // Allow 350ms natural gap between words/syllables before resetting timer
            if (speechStartTimestamp > 0) {
              if (silenceStartTimestamp === 0) {
                silenceStartTimestamp = now
              } else if (now - silenceStartTimestamp > 350) {
                speechStartTimestamp = 0
                silenceStartTimestamp = 0
              }
            }
          }
        } else {
          speechStartTimestamp = 0
          silenceStartTimestamp = 0
        }

        requestAnimationFrame(checkAudioLevel)
      }
      checkAudioLevel()

      // Worklet Node for raw PCM acquisition
      const blob = new Blob([WORKLET_CODE], { type: 'application/javascript' })
      const url = URL.createObjectURL(blob)
      await this.audioContext.audioWorklet.addModule(url)

      this.workletNode = new AudioWorkletNode(this.audioContext, 'pcm-processor')
      this.mediaSourceNode.connect(this.workletNode)

      this.workletNode.port.onmessage = (event) => {
        const int16 = event.data
        this.sendAudioChunk(int16)
      }
    } catch (err) {
      console.error('Failed to access microphone or initialize AudioContext:', err)
    }
  }

  private stopMic() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop())
      this.mediaStream = null
    }
    if (this.workletNode) {
      this.workletNode.disconnect()
      this.workletNode = null
    }
    if (this.mediaSourceNode) {
      this.mediaSourceNode.disconnect()
      this.mediaSourceNode = null
    }
  }

  private sendAudioChunk(int16Array: Int16Array) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return

    // Convert Int16Array to base64
    const buffer = int16Array.buffer
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    const base64 = btoa(binary)

    const audioMsg = {
      realtimeInput: {
        audio: {
          mimeType: 'audio/pcm;rate=16000',
          data: base64
        }
      }
    }

    this.ws.send(JSON.stringify(audioMsg))
  }

  private async handleServerMessage(msg: any) {
    // 0. Server Interruption signal
    if (msg.serverContent?.interrupted) {
      this.audioQueue?.stopAll()
    }

    // 1. Handle Audio output
    const parts = msg.serverContent?.modelTurn?.parts
    if (parts) {
      for (const part of parts) {
        if (part.inlineData) {
          const base64 = part.inlineData.data
          const binary = atob(base64)
          const bytes = new Uint8Array(binary.length)
          for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i)
          }
          const int16 = new Int16Array(bytes.buffer)
          this.audioQueue?.playChunk(int16)
        }

        if (part.text && this.onTranscription) {
          this.onTranscription('model', part.text, true)
        }
      }
    }

    // 2. Handle transcription parts from user speech
    const userParts = msg.serverContent?.turnComplete
    if (userParts && this.onTranscription) {
      // Finished speaking
    }

    // 3. Handle Tool call
    const toolCall = msg.toolCall
    if (toolCall && toolCall.functionCalls) {
      for (const fc of toolCall.functionCalls) {
        const response = await this.executeToolCall(fc.name, fc.args)
        this.sendToolResponse(fc.id, response)
      }
    }
  }

  private async executeToolCall(name: string, args: any) {
    try {
      const res = await dispatchAIFunction(name, args)
      if (this.onToolExecution) {
        this.onToolExecution({
          action: name,
          requests: res.requests || [],
          message: res.message || 'Amal bajarildi.',
          data: res.data
        })
      }
      if (res && res.code === 0) {
        return { code: 0, message: res.message || 'Success', data: res.data }
      }
      return { code: 500, message: (res as any).message || 'Execution failed' }
    } catch (err: any) {
      return { code: 500, message: err.message }
    }
  }

  private sendToolResponse(callId: string, output: any) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return

    const respMsg = {
      toolResponse: {
        functionResponses: [
          {
            response: { output },
            id: callId
          }
        ]
      }
    }

    this.ws.send(JSON.stringify(respMsg))
  }
}
