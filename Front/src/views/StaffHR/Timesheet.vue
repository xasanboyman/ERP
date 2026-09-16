<template>
  <ContentWrap>
    <!-- Header Controls -->
    <div class="mb-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <el-radio-group v-model="viewMode" size="default">
          <el-radio-button value="cubic">
            <Icon icon="vi-ep:grid" class="mr-1 inline-block align-middle" />
            Kubik Tabel (Oylik matrisa)
          </el-radio-button>
          <el-radio-button value="list">
            <Icon icon="vi-ep:document" class="mr-1 inline-block align-middle" />
            Ro'yxat ko'rinishi
          </el-radio-button>
        </el-radio-group>
      </div>

      <div class="flex items-center flex-wrap gap-2">
        <!-- If in list mode: New Timesheet Button -->
        <el-button v-if="viewMode === 'list'" type="primary" @click="openAddDialog">
          <Icon icon="vi-ep:plus" class="mr-1" />
          {{ t('erp.newTimesheetBtn') }}
        </el-button>

        <!-- If in cubic mode: Action buttons -->
        <template v-else>
          <el-button-group>
            <el-button :disabled="cubicLoading" @click="changeMonth(-1)">
              <Icon icon="vi-ep:arrow-left" />
            </el-button>
            <el-date-picker
              v-model="selectedMonth"
              type="month"
              value-format="YYYY-MM"
              :clearable="false"
              placeholder="Oyni tanlang"
              style="width: 140px"
              @change="onMonthChange"
            />
            <el-button :disabled="cubicLoading" @click="changeMonth(1)">
              <Icon icon="vi-ep:arrow-right" />
            </el-button>
          </el-button-group>

          <el-button type="success" :loading="savingCubic" @click="saveCubicTimesheet">
            <Icon icon="vi-ep:check" class="mr-1" />
            Saqlash
          </el-button>

          <el-button type="warning" plain @click="autoFillWorkdays">
            <Icon icon="vi-ep:magic-stick" class="mr-1" />
            Avto-to'ldirish (8 soat)
          </el-button>

          <el-button type="info" plain @click="clearMonthGrid">
            <Icon icon="vi-ep:refresh" class="mr-1" />
            Tozalash
          </el-button>
        </template>
      </div>
    </div>

    <!-- ==================== CUBIC TABLE VIEW ==================== -->
    <div v-if="viewMode === 'cubic'" class="space-y-4">
      <!-- Legend Bar -->
      <div
        class="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700/60 text-xs"
      >
        <div class="flex flex-wrap items-center gap-4 text-slate-600 dark:text-slate-300">
          <span class="font-bold text-slate-700 dark:text-slate-200">Belgilar:</span>
          <span class="inline-flex items-center gap-1.5">
            <span
              class="w-5 h-5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold inline-flex items-center justify-center text-[11px]"
              >8</span
            >
            Keldi (Ishladi)
          </span>
          <span class="inline-flex items-center gap-1.5">
            <span
              class="w-5 h-5 rounded bg-rose-100 text-rose-800 border border-rose-300 font-bold inline-flex items-center justify-center text-[11px]"
              >Y</span
            >
            Kelmagan (Yo'q)
          </span>
          <span class="inline-flex items-center gap-1.5">
            <span
              class="w-5 h-5 rounded bg-amber-100 text-amber-800 border border-amber-300 font-bold inline-flex items-center justify-center text-[11px]"
              >K</span
            >
            Kasal (Betob)
          </span>
          <span class="inline-flex items-center gap-1.5">
            <span
              class="w-5 h-5 rounded bg-sky-100 text-sky-800 border border-sky-300 font-bold inline-flex items-center justify-center text-[11px]"
              >T</span
            >
            Ta'tilda
          </span>
          <span class="inline-flex items-center gap-1.5">
            <span
              class="w-5 h-5 rounded bg-slate-100 text-slate-500 border border-slate-200 font-medium inline-flex items-center justify-center text-[11px]"
              >D</span
            >
            Dam olish
          </span>
        </div>
        <div class="text-slate-500 dark:text-slate-400 italic">
          Katak ustiga bosib xodim holatini yoki soatini o'zgartiring
        </div>
      </div>

      <!-- Empty State when 0 workers -->
      <div
        v-if="!workers.length && !loading"
        class="py-14 flex flex-col items-center justify-center text-center bg-white dark:bg-[#1f222d] rounded-xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm"
      >
        <div
          class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 text-primary"
        >
          <Icon icon="vi-ep:user" class="text-3xl" />
        </div>
        <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-1">
          Xodimlar mavjud emas
        </h3>
        <p class="text-sm text-slate-500 max-w-md mb-6">
          Ushbu tashkilotda hali xodimlar mavjud emas. Kubik tabelni yuritish va davomatni belgilash
          uchun avval xodimlarni ro'yxatdan o'tkazing.
        </p>
        <el-button type="primary" @click="goToWorkers">
          <Icon icon="vi-ep:plus" class="mr-1" />
          Xodimlar bo'limiga o'tish
        </el-button>
      </div>

      <!-- Cubic Matrix Table -->
      <div v-else class="rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
        <el-table
          v-loading="loading || cubicLoading"
          :data="cubicTableRows"
          border
          stripe
          style="width: 100%"
          class="cubic-table"
          max-height="650"
        >
          <el-table-column type="index" label="#" width="45" align="center" fixed="left" />
          <el-table-column
            prop="name"
            label="Xodim F.I.Sh."
            width="170"
            fixed="left"
            show-overflow-tooltip
          >
            <template #default="scope">
              <div class="font-medium text-slate-800 dark:text-slate-200 leading-snug">
                {{ scope.row.name }}
              </div>
              <div class="text-[11px] text-slate-400 font-mono">{{ scope.row.workerId }}</div>
            </template>
          </el-table-column>
          <el-table-column
            prop="role"
            label="Lavozimi"
            width="130"
            fixed="left"
            show-overflow-tooltip
          >
            <template #default="scope">
              <el-tag size="small" type="info">{{ scope.row.role || 'Xodim' }}</el-tag>
            </template>
          </el-table-column>

          <!-- Dynamic 1..31 Day Columns -->
          <el-table-column
            v-for="day in daysInMonth"
            :key="day.dayNumber"
            :label="String(day.dayNumber)"
            width="46"
            align="center"
            :class-name="day.isWeekend ? 'weekend-column' : ''"
          >
            <template #header>
              <div
                :class="[
                  'text-center leading-none select-none py-0.5',
                  day.isWeekend
                    ? 'text-rose-600 font-bold'
                    : 'text-slate-600 dark:text-slate-300 font-medium'
                ]"
              >
                <div class="text-[12px]">{{ day.dayNumber }}</div>
                <div class="text-[9px] uppercase tracking-tighter opacity-80 mt-0.5">
                  {{ day.dayShort }}
                </div>
              </div>
            </template>
            <template #default="scope">
              <div
                class="cubic-cell select-none mx-auto flex items-center justify-center rounded cursor-pointer transition-transform duration-100 active:scale-95"
                :class="
                  getCubicStyle(
                    scope.row.days[day.dayNumber]?.status,
                    scope.row.days[day.dayNumber]?.hours,
                    day.isWeekend
                  )
                "
                @click="handleCellClick(scope.row, day.dayNumber)"
              >
                {{
                  getCubicText(
                    scope.row.days[day.dayNumber]?.status,
                    scope.row.days[day.dayNumber]?.hours,
                    day.isWeekend
                  )
                }}
              </div>
            </template>
          </el-table-column>

          <!-- Right Frozen Summary Columns -->
          <el-table-column label="Ish kuni" width="80" align="center" fixed="right">
            <template #default="scope">
              <span class="font-bold text-emerald-600 dark:text-emerald-400">
                {{ calculatePresentDays(scope.row) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Kelmadi" width="75" align="center" fixed="right">
            <template #default="scope">
              <span class="font-bold text-rose-500 dark:text-rose-400">
                {{ calculateAbsentDays(scope.row) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Jami soat" width="90" align="center" fixed="right">
            <template #default="scope">
              <span class="font-bold text-primary"> {{ calculateTotalHours(scope.row) }} s </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- ==================== LIST TABLE VIEW ==================== -->
    <div v-else>
      <el-table v-loading="loading" :data="tableData" style="width: 100%" border stripe>
        <el-table-column type="expand">
          <template #default="props">
            <div class="p-4 bg-slate-50/70 dark:bg-slate-800/40 rounded-lg border border-slate-100 dark:border-slate-800">
              <h3 class="font-bold mb-2 text-slate-800 dark:text-slate-100">Xodimlar davomati:</h3>
              <el-table :data="props.row.records" size="small" border>
                <el-table-column prop="workerName" label="Ismi" min-width="150" />
                <el-table-column prop="status" label="Ishtiroki" width="150">
                  <template #default="scope">
                    <el-tag :type="getAttendanceTagType(scope.row.status)">
                      {{ getAttendanceLabel(scope.row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="hours" label="Ish soati" width="120" align="center" />
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="date" :label="t('erp.timesheetDate')" width="160" />
        <el-table-column
          prop="records.length"
          :label="t('erp.workerCount')"
          width="160"
          align="center"
        >
          <template #default="scope">
            {{ scope.row.records ? scope.row.records.length : 0 }} nafar
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          :label="t('erp.timesheetStatus')"
          width="150"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="scope.row.status === 'archived' ? 'info' : 'success'">
              {{ scope.row.status === 'archived' ? 'Arxivlangan' : 'Faol' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" :label="t('erp.createdTime')" min-width="180" />
        <el-table-column :label="t('erp.amallar')" width="180" fixed="right">
          <template #default="scope">
            <el-button
              link
              type="primary"
              :disabled="scope.row.status === 'archived'"
              @click="openEditDialog(scope.row)"
            >
              {{ t('common.edit') }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(scope.row)">
              {{ t('common.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ==================== CELL EDIT DIALOG ==================== -->
    <el-dialog
      v-model="cellDialogVisible"
      :title="`Kunlik davomat: ${activeCell?.worker?.name || ''}`"
      width="400px"
      destroy-on-close
    >
      <div v-if="activeCell" class="space-y-4">
        <div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-sm border border-slate-100 dark:border-slate-700">
          <div class="flex items-center justify-between">
            <span class="text-slate-500">Sana:</span>
            <span class="font-bold text-slate-800 dark:text-slate-100">{{ activeCell.dateStr }}</span>
          </div>
          <div class="flex items-center justify-between mt-1">
            <span class="text-slate-500">Hozirgi holat:</span>
            <el-tag size="small" :type="getAttendanceTagType(activeCell.currentStatus)">
              {{ getAttendanceLabel(activeCell.currentStatus) || 'Dam olish' }}
            </el-tag>
          </div>
        </div>

        <div class="text-xs font-semibold text-slate-600 dark:text-slate-300">
          Tezkor belgilash:
        </div>

        <div class="grid grid-cols-2 gap-2">
          <el-button
            type="success"
            class="!h-11 !justify-start"
            @click="applyCellStatus('present', 8)"
          >
            <span
              class="w-6 h-6 rounded bg-emerald-600 text-white font-bold inline-flex items-center justify-center mr-2 text-xs"
              >8</span
            >
            Keldi (8 soat)
          </el-button>

          <el-button
            type="danger"
            class="!h-11 !justify-start"
            @click="applyCellStatus('absent', 0)"
          >
            <span
              class="w-6 h-6 rounded bg-rose-600 text-white font-bold inline-flex items-center justify-center mr-2 text-xs"
              >Y</span
            >
            Kelmadi (Yo'q)
          </el-button>

          <el-button
            type="warning"
            class="!h-11 !justify-start"
            @click="applyCellStatus('sick', 0)"
          >
            <span
              class="w-6 h-6 rounded bg-amber-600 text-white font-bold inline-flex items-center justify-center mr-2 text-xs"
              >K</span
            >
            Kasal (Betob)
          </el-button>

          <el-button
            type="primary"
            class="!h-11 !justify-start"
            @click="applyCellStatus('leave', 0)"
          >
            <span
              class="w-6 h-6 rounded bg-sky-600 text-white font-bold inline-flex items-center justify-center mr-2 text-xs"
              >T</span
            >
            Ta'tilda
          </el-button>

          <el-button
            type="info"
            class="!h-11 !justify-start"
            @click="applyCellStatus('dayoff', 0)"
          >
            <span
              class="w-6 h-6 rounded bg-slate-500 text-white font-bold inline-flex items-center justify-center mr-2 text-xs"
              >D</span
            >
            Dam olish
          </el-button>

          <el-button
            plain
            class="!h-11 !justify-start"
            @click="applyCellStatus('', 0)"
          >
            <span
              class="w-6 h-6 rounded border border-slate-300 text-slate-500 font-bold inline-flex items-center justify-center mr-2 text-xs"
              >-</span
            >
            Tozalash
          </el-button>
        </div>

        <div class="pt-3 border-t border-slate-100 dark:border-slate-800">
          <div class="text-xs text-slate-500 mb-2 font-medium">
            Boshqa ish soati belgilash (masalan 4, 6, 12):
          </div>
          <div class="flex items-center gap-2">
            <el-input-number
              v-model="activeCell.currentHours"
              :min="0"
              :max="24"
              :step="1"
              size="default"
              style="width: 140px"
            />
            <el-button
              type="primary"
              @click="applyCellStatus('present', activeCell.currentHours)"
            >
              Belgilash
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- ==================== LIST ADD/EDIT DIALOG ==================== -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? 'Yangi tabel kiritish' : 'Tabelni tahrirlash'"
      width="750px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <div class="grid grid-cols-2 gap-4">
          <el-form-item :label="t('erp.timesheetDate')" prop="date">
            <el-date-picker
              v-model="form.date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="Sana tanlang"
              style="width: 100%"
              :disabled="dialogType === 'edit'"
            />
          </el-form-item>
          <el-form-item :label="t('erp.holati')" prop="status">
            <el-radio-group v-model="form.status">
              <el-radio value="active">{{ t('erp.faol') }}</el-radio>
              <el-radio value="archived">Arxivlash</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <el-divider>Xodimlar ro'yxati va davomati</el-divider>

        <el-table :data="form.records" size="small" style="width: 100%" max-height="300">
          <el-table-column prop="workerName" label="Ismi" />
          <el-table-column label="Davomati" width="200">
            <template #default="scope">
              <el-select v-model="scope.row.status" placeholder="Tanlang" size="small">
                <el-option label="Keldi (Present)" value="present" />
                <el-option label="Kelmagan (Absent)" value="absent" />
                <el-option label="Kasal (Sick)" value="sick" />
                <el-option label="Ta'til (Leave)" value="leave" />
                <el-option label="Dam olish (Day off)" value="dayoff" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Ish soati" width="180">
            <template #default="scope">
              <el-input-number
                v-model="scope.row.hours"
                :min="0"
                :max="24"
                :step="1"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">{{
          t('common.save')
        }}</el-button>
      </template>
    </el-dialog>
  </ContentWrap>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '@/hooks/web/useI18n'
import { ContentWrap } from '@/components/ContentWrap'
import { Icon } from '@/components/Icon'
import dayjs from 'dayjs'
import {
  ElMessage,
  ElMessageBox,
  ElButton,
  ElButtonGroup,
  ElTable,
  ElTableColumn,
  ElTag,
  ElDialog,
  ElForm,
  ElFormItem,
  ElDatePicker,
  ElRadioGroup,
  ElRadioButton,
  ElRadio,
  ElDivider,
  ElSelect,
  ElOption,
  ElInputNumber
} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getTimesheetListApi, saveTimesheetApi, deleteTimesheetApi } from '@/api/staff_hr'
import { getWorkerListApi } from '@/api/worker'
import { useRealtimeSync } from '@/hooks/web/useRealtimeSync'

const { t } = useI18n()
const router = useRouter()

// View Mode
const viewMode = ref<'cubic' | 'list'>('cubic')

// General State
const loading = ref(false)
const tableData = ref<any[]>([])
const workers = ref<any[]>([])

// Realtime sync
useRealtimeSync(['staff_hr', 'staff_timesheet', 'timesheet', 'worker'], () => {
  getList()
  getWorkers()
})

const goToWorkers = () => {
  router.push('/hr/workers')
}

// ---------------- CUBIC MATRIX LOGIC ----------------
const selectedMonth = ref<string>(dayjs().format('YYYY-MM'))
const cubicLoading = ref(false)
const savingCubic = ref(false)

const WEEKDAYS_UZ = ['Ya', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh']

interface DayColumnInfo {
  dayNumber: number
  date: string
  dayShort: string
  isWeekend: boolean
}

const daysInMonth = computed<DayColumnInfo[]>(() => {
  if (!selectedMonth.value) return []
  const [year, month] = selectedMonth.value.split('-').map(Number)
  const count = dayjs(`${year}-${month}-01`).daysInMonth()
  const list: DayColumnInfo[] = []
  for (let d = 1; d <= count; d++) {
    const dateStr = `${selectedMonth.value}-${String(d).padStart(2, '0')}`
    const dayOfWeek = dayjs(dateStr).day()
    list.push({
      dayNumber: d,
      date: dateStr,
      dayShort: WEEKDAYS_UZ[dayOfWeek],
      isWeekend: dayOfWeek === 0 || dayOfWeek === 6
    })
  }
  return list
})

interface WorkerDayData {
  status: string
  hours: number
  modified?: boolean
}

interface CubicRow {
  workerId: string
  name: string
  role: string
  department: string
  days: Record<number, WorkerDayData>
}

const cubicTableRows = ref<CubicRow[]>([])

const buildCubicGrid = () => {
  if (!workers.value.length) {
    cubicTableRows.value = []
    return
  }

  const rows: CubicRow[] = []
  for (const w of workers.value) {
    const row: CubicRow = {
      workerId: w.id,
      name: w.name,
      role: w.role || 'Xodim',
      department: w.department || '',
      days: {}
    }

    for (const d of daysInMonth.value) {
      row.days[d.dayNumber] = {
        status: d.isWeekend ? 'dayoff' : '',
        hours: 0
      }
    }

    rows.push(row)
  }

  // Map existing timesheets in tableData for the selectedMonth
  for (const t of tableData.value) {
    if (t.date && t.date.startsWith(selectedMonth.value)) {
      const parts = t.date.split('-')
      const dayNum = parseInt(parts[2], 10)
      if (Array.isArray(t.records)) {
        for (const r of t.records) {
          const row = rows.find(
            (x) =>
              x.workerId === r.workerId ||
              x.name.toLowerCase() === (r.workerName || '').toLowerCase()
          )
          if (row && row.days[dayNum]) {
            row.days[dayNum] = {
              status: r.status || (r.hours > 0 ? 'present' : 'absent'),
              hours: r.hours !== undefined ? r.hours : r.status === 'present' ? 8 : 0
            }
          }
        }
      }
    }
  }

  cubicTableRows.value = rows
}

const changeMonth = (delta: number) => {
  const next = dayjs(selectedMonth.value + '-01')
    .add(delta, 'month')
    .format('YYYY-MM')
  selectedMonth.value = next
  buildCubicGrid()
}

const onMonthChange = () => {
  buildCubicGrid()
}

// Styling helpers
const getCubicText = (status?: string, hours?: number, isWeekend?: boolean) => {
  if (!status) {
    return isWeekend ? 'D' : '-'
  }
  if (status === 'present') {
    return hours ? String(hours) : '8'
  }
  if (status === 'absent') return 'Y'
  if (status === 'sick') return 'K'
  if (status === 'leave') return 'T'
  if (status === 'dayoff') return 'D'
  return '-'
}

const getCubicStyle = (status?: string, hours?: number, isWeekend?: boolean) => {
  if (!status) {
    if (isWeekend) {
      return 'bg-slate-100/70 text-slate-400 border border-slate-200 dark:bg-slate-800/40 dark:text-slate-500 dark:border-slate-700'
    }
    return 'bg-white text-slate-300 border border-dashed border-slate-200 hover:border-primary hover:text-primary dark:bg-slate-900/30 dark:border-slate-700'
  }
  if (status === 'present') {
    return 'bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold hover:bg-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-700'
  }
  if (status === 'absent') {
    return 'bg-rose-100 text-rose-800 border border-rose-300 font-bold hover:bg-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-700'
  }
  if (status === 'sick') {
    return 'bg-amber-100 text-amber-800 border border-amber-300 font-bold hover:bg-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-700'
  }
  if (status === 'leave') {
    return 'bg-sky-100 text-sky-800 border border-sky-300 font-bold hover:bg-sky-200 dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-700'
  }
  if (status === 'dayoff') {
    return 'bg-slate-100 text-slate-500 border border-slate-200 font-medium hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
  }
  return 'bg-slate-50 text-slate-400 border border-slate-200'
}

// Calculations
const calculatePresentDays = (row: CubicRow) => {
  let count = 0
  for (const d of Object.values(row.days)) {
    if (d.status === 'present' || (d.hours && d.hours > 0)) {
      count++
    }
  }
  return count
}

const calculateAbsentDays = (row: CubicRow) => {
  let count = 0
  for (const d of Object.values(row.days)) {
    if (d.status === 'absent') {
      count++
    }
  }
  return count
}

const calculateTotalHours = (row: CubicRow) => {
  let total = 0
  for (const d of Object.values(row.days)) {
    if (d.hours) {
      total += Number(d.hours)
    } else if (d.status === 'present') {
      total += 8
    }
  }
  return total
}

// Auto fill
const autoFillWorkdays = () => {
  if (!cubicTableRows.value.length) {
    ElMessage.warning("Tashkilotda xodimlar mavjud emas")
    return
  }
  for (const row of cubicTableRows.value) {
    for (const day of daysInMonth.value) {
      if (day.isWeekend) {
        row.days[day.dayNumber] = { status: 'dayoff', hours: 0, modified: true }
      } else {
        row.days[day.dayNumber] = { status: 'present', hours: 8, modified: true }
      }
    }
  }
  ElMessage.success("Barcha ish kunlariga 8 soat belgilandi. Saqlash tugmasini bosing!")
}

// Clear grid
const clearMonthGrid = () => {
  ElMessageBox.confirm(
    "Ushbu oy uchun kiritilgan davomat belgilarini tozalashni tasdiqlaysizmi?",
    'Ogohlantirish',
    {
      confirmButtonText: 'Tasdiqlash',
      cancelButtonText: 'Bekor qilish',
      type: 'warning'
    }
  )
    .then(() => {
      for (const row of cubicTableRows.value) {
        for (const day of daysInMonth.value) {
          row.days[day.dayNumber] = {
            status: day.isWeekend ? 'dayoff' : '',
            hours: 0,
            modified: true
          }
        }
      }
      ElMessage.info('Davomat kataklari tozalandi')
    })
    .catch(() => {})
}

// Save Cubic Matrix
const saveCubicTimesheet = async () => {
  if (!workers.value.length) {
    ElMessage.warning('Tashkilotda saqlash uchun xodimlar mavjud emas')
    return
  }
  savingCubic.value = true
  try {
    const promises: Promise<any>[] = []
    for (const day of daysInMonth.value) {
      const records = cubicTableRows.value.map((row) => {
        const dayCell = row.days[day.dayNumber] || {}
        let st = dayCell.status
        let hrs = dayCell.hours || 0
        if (!st) {
          st = day.isWeekend ? 'dayoff' : 'present'
          hrs = day.isWeekend ? 0 : 8
        }
        return {
          workerId: row.workerId,
          workerName: row.name,
          status: st,
          hours: hrs
        }
      })
      const existing = tableData.value.find((t) => t.date === day.date)
      promises.push(
        saveTimesheetApi({
          id: existing?.id || '',
          date: day.date,
          status: 'active',
          records
        })
      )
    }
    await Promise.all(promises)
    ElMessage.success(`${selectedMonth.value} oyi uchun kubik tabel muvaffaqiyatli saqlandi!`)
    await getList()
  } catch (err) {
    console.error(err)
    ElMessage.error('Tabelni saqlashda xatolik yuz berdi')
  } finally {
    savingCubic.value = false
  }
}

// Cell click & quick popover/dialog
const activeCell = ref<{
  worker: CubicRow
  dayNumber: number
  dateStr: string
  currentStatus: string
  currentHours: number
} | null>(null)
const cellDialogVisible = ref(false)

const handleCellClick = (workerRow: CubicRow, dayNumber: number) => {
  const dayInfo = daysInMonth.value.find((d) => d.dayNumber === dayNumber)
  const cell = workerRow.days[dayNumber] || {
    status: dayInfo?.isWeekend ? 'dayoff' : '',
    hours: 0
  }
  activeCell.value = {
    worker: workerRow,
    dayNumber,
    dateStr: dayInfo?.date || '',
    currentStatus: cell.status || (dayInfo?.isWeekend ? 'dayoff' : 'present'),
    currentHours: cell.hours ?? (cell.status === 'present' ? 8 : 0)
  }
  cellDialogVisible.value = true
}

const applyCellStatus = (status: string, hours: number) => {
  if (!activeCell.value) return
  const { worker, dayNumber } = activeCell.value
  worker.days[dayNumber] = {
    status,
    hours,
    modified: true
  }
  cellDialogVisible.value = false
}

// ---------------- LIST VIEW LOGIC ----------------
const getList = async () => {
  loading.value = true
  try {
    const res = await getTimesheetListApi()
    if (res && res.code === 0) {
      tableData.value = res.data.list || []
      buildCubicGrid()
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getWorkers = async () => {
  try {
    const res = await getWorkerListApi({ pageIndex: 1, pageSize: 100 })
    if (res && res.code === 0) {
      workers.value = res.data.list || []
      buildCubicGrid()
    }
  } catch (err) {
    console.error(err)
  }
}

// Dialog Logic for List View
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: '',
  date: '',
  status: 'active',
  records: [] as any[]
})

const rules = reactive<FormRules>({
  date: [{ required: true, message: 'Iltimos, tabel sanasini tanlang', trigger: 'blur' }]
})

const openAddDialog = () => {
  dialogType.value = 'add'
  form.id = ''
  form.date = new Date().toISOString().split('T')[0]
  form.status = 'active'
  form.records = workers.value.map((w) => ({
    workerId: w.id,
    workerName: w.name,
    status: 'present',
    hours: 8
  }))
  dialogVisible.value = true
}

const openEditDialog = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.date = row.date
  form.status = row.status
  form.records = JSON.parse(JSON.stringify(row.records))
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const res = await saveTimesheetApi(form)
        if (res && res.code === 0) {
          ElMessage.success('Tabel muvaffaqiyatli saqlandi')
          dialogVisible.value = false
          getList()
        }
      } catch (err) {
        console.error(err)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm("Ushbu tabelni o'chirishni tasdiqlaysizmi?", 'Eslatma', {
    confirmButtonText: 'Tasdiqlash',
    cancelButtonText: 'Bekor qilish',
    type: 'warning'
  })
    .then(async () => {
      const res = await deleteTimesheetApi({ ids: [row.id] })
      if (res && res.code === 0) {
        ElMessage.success("Tabel o'chirildi")
        getList()
      }
    })
    .catch(() => {})
}

// Helpers
const getAttendanceLabel = (status: string) => {
  const map: Record<string, string> = {
    present: 'Keldi',
    absent: 'Kelmagan',
    sick: 'Kasal',
    leave: "Ta'tilda",
    dayoff: 'Dam olish'
  }
  return map[status] || status
}

const getAttendanceTagType = (
  status: string
): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    present: 'success',
    absent: 'danger',
    sick: 'warning',
    leave: 'primary',
    dayoff: 'info'
  }
  return map[status] || 'info'
}

onMounted(() => {
  getList()
  getWorkers()
})
</script>

<style scoped>
.weekend-column {
  background-color: rgba(244, 63, 94, 0.04) !important;
}

.cubic-cell {
  width: 32px;
  height: 32px;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
}

.cubic-cell:hover {
  transform: scale(1.08);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12);
}

:deep(.cubic-table .el-table__header th) {
  padding: 4px 0 !important;
}

:deep(.cubic-table .el-table__body td) {
  padding: 4px 0 !important;
}
</style>
