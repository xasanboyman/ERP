#!/usr/bin/env python3
"""
Convert all hardcoded text in Analysis.vue to reactive t('...') i18n calls.
"""

filepath = '/home/xasanboy/ERP/Front/src/views/Dashboard/Analysis.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add locale store import & watcher if not present
if 'useLocaleStore' not in content:
    content = content.replace(
        "import { useI18n } from '@/hooks/web/useI18n'",
        "import { useI18n } from '@/hooks/web/useI18n'\nimport { useLocaleStore } from '@/store/modules/locale'"
    )
    content = content.replace(
        "const isDark = computed(() => appStore.getIsDark)",
        "const isDark = computed(() => appStore.getIsDark)\nconst localeStore = useLocaleStore()\n\nwatch(\n  () => localeStore.getCurrentLocale,\n  () => {\n    buildChartOptions()\n    buildArchiveCharts()\n    updateComparisonCalculations()\n  }\n)"
    )

# SCRIPT UPDATES
# 1. period labels in updateComparisonCalculations
old_compare_logic = """  if (comparePreset.value === 'mom') {
    period1Label.value = 'Август 2026 (Ушбу ой)'
    period2Label.value = 'Июл 2026 (Ўтган ой)'
    p1Mult = 1.22
    p2Mult = 1.14
  } else if (comparePreset.value === 'qoq') {
    period1Label.value = '3-Чорак 2026 (Q3)'
    period2Label.value = '2-Чорак 2026 (Q2)'
    p1Mult = 1.35
    p2Mult = 1.1
  } else if (comparePreset.value === 'last30') {
    period1Label.value = 'Охирги 30 кун'
    period2Label.value = 'Олдинги 30 кун'
    p1Mult = 1.18
    p2Mult = 1.05
  } else if (comparePreset.value === 'yoy') {
    period1Label.value = '2026 Йиллик натижалар'
    period2Label.value = '2025 Йиллик натижалар'
    p1Mult = 1.45
    p2Mult = 1.0
  } else if (comparePreset.value === 'custom') {
    const p1Text = period1Dates.value
      ? `${period1Dates.value[0]} ~ ${period1Dates.value[1]}`
      : '1-Давр'
    const p2Text = period2Dates.value
      ? `${period2Dates.value[0]} ~ ${period2Dates.value[1]}`
      : '2-Давр'
    period1Label.value = `1-Давр (${p1Text})`
    period2Label.value = `2-Давр (${p2Text})`
    p1Mult = 1.25
    p2Mult = 1.02
  }"""

new_compare_logic = """  if (comparePreset.value === 'mom') {
    period1Label.value = `${t('analysis.august')} 2026 (${t('erp.currentMonthPill')})`
    period2Label.value = `${t('analysis.july')} 2026 (${t('erp.prevMonthPill')})`
    p1Mult = 1.22
    p2Mult = 1.14
  } else if (comparePreset.value === 'qoq') {
    period1Label.value = `3-Q 2026 (Q3)`
    period2Label.value = `2-Q 2026 (Q2)`
    p1Mult = 1.35
    p2Mult = 1.1
  } else if (comparePreset.value === 'last30') {
    period1Label.value = t('analysis.compareLast30')
    period2Label.value = `${t('erp.prevMonthPill')} (30d)`
    p1Mult = 1.18
    p2Mult = 1.05
  } else if (comparePreset.value === 'yoy') {
    period1Label.value = `2026 (${t('analysis.yearly')})`
    period2Label.value = `2025 (${t('analysis.yearly')})`
    p1Mult = 1.45
    p2Mult = 1.0
  } else if (comparePreset.value === 'custom') {
    const p1Text = period1Dates.value
      ? `${period1Dates.value[0]} ~ ${period1Dates.value[1]}`
      : t('analysis.period1')
    const p2Text = period2Dates.value
      ? `${period2Dates.value[0]} ~ ${period2Dates.value[1]}`
      : t('analysis.period2')
    period1Label.value = `${t('analysis.period1')} (${p1Text})`
    period2Label.value = `${t('analysis.period2')} (${p2Text})`
    p1Mult = 1.25
    p2Mult = 1.02
  }"""

if old_compare_logic in content:
    content = content.replace(old_compare_logic, new_compare_logic)
    print("✓ Replaced compare preset logic in script")

# Initial ref values
content = content.replace("const period1Label = ref('Август 2026 (Ушбу ой)')", "const period1Label = ref('Period 1')")
content = content.replace("const period2Label = ref('Июл 2026 (Ўтган ой)')", "const period2Label = ref('Period 2')")

# Month names in buildArchiveCharts
old_months_archive = "const months = ['Март', 'Апрел', 'Май', 'Июн', 'Июл', 'Август']"
new_months_archive = "const months = [t('analysis.march'), t('analysis.april'), t('analysis.may'), t('analysis.june'), t('analysis.july'), t('analysis.august')]"
content = content.replace(old_months_archive, new_months_archive)

# Categories in buildComparisonChartOptions
old_categories = "const categories = ['Жами Тушум', t('erp.costCogs'), 'Иш Ҳақи', t('erp.realNetProfit')]"
new_categories = "const categories = [t('analysis.grossRevenue'), t('erp.costCogs'), t('analysis.totalPayroll'), t('erp.realNetProfit')]"
content = content.replace(old_categories, new_categories)

# Donut data in buildComparisonChartOptions
old_pie_payroll = "name: 'Иш Ҳақи (Payroll)'"
new_pie_payroll = "name: t('analysis.totalPayroll')"
content = content.replace(old_pie_payroll, new_pie_payroll)
old_pie_profit = "name: 'Соф Фойда (Profit)'"
new_pie_profit = "name: t('erp.realNetProfit')"
content = content.replace(old_pie_profit, new_pie_profit)

# Archive donut in buildArchiveCharts
content = content.replace("name: 'Маҳсулот Таннархи (COGS)'", "name: t('erp.costCogs')")
content = content.replace("name: `Доимий ${t('erp.salaries')} & Аванслар`", "name: `${t('analysis.permanentSalaries')} & Avans`")
content = content.replace("name: 'Қисқа Муддатли Ишчилар'", "name: t('analysis.shortTermWorkers')")
content = content.replace("name: 'Молиявий Тақсимот'", "name: t('erp.financialDistributionRing')")

# Quick jump months
old_quick_jump = """const quickJumpMonths = computed(() => {
  const current = getCurrentMonth()
  const last = getLastMonth()
  return [
    {
      label: 'Жорий Ой (Август)',
      value: current,
      tip: '2026-08 ойи тушуми ва жорий ойдаги савдоларни кўриш'
    },
    {
      label: 'Ўтган Ой (Июл)',
      value: last,
      tip: '2026-07 ойи якуний ҳисоботини кўриш ёки муҳрлаш'
    },
    { label: 'Июн 2026', value: '2026-06', tip: '2026-06 ойи архив ва савдо кўрсаткичлари' },
    { label: 'Май 2026', value: '2026-05', tip: '2026-05 ойи архив ва савдо кўрсаткичлари' }
  ]
})"""

new_quick_jump = """const quickJumpMonths = computed(() => {
  const current = getCurrentMonth()
  const last = getLastMonth()
  return [
    {
      label: `${t('erp.currentMonthPill')} (${t('analysis.august')})`,
      value: current,
      tip: `2026-08 ${t('analysis.tipSelectMonth')}`
    },
    {
      label: `${t('erp.prevMonthPill')} (${t('analysis.july')})`,
      value: last,
      tip: `2026-07 ${t('analysis.tipSelectMonth')}`
    },
    { label: `${t('analysis.june')} 2026`, value: '2026-06', tip: `2026-06 ${t('analysis.tipSelectMonth')}` },
    { label: `${t('analysis.may')} 2026`, value: '2026-05', tip: `2026-05 ${t('analysis.tipSelectMonth')}` }
  ]
})"""
if old_quick_jump in content:
    content = content.replace(old_quick_jump, new_quick_jump)
    print("✓ Replaced quick jump months")

# Comparison table rows
old_comp_table = """  // 5. Update Comparison Table Data with clear descriptions and hover tooltips
  comparisonTable.value = [
    {
      metric: 'Жами Тушум (Gross Revenue)',
      p1: p1Rev,
      p2: p2Rev,
      diff: revDiff,
      growth: revGrowth,
      status: revGrowth >= 0 ? 'positive' : 'negative',
      desc: 'Барча сотилган товарлардан тушган ялпи даромад',
      tooltip:
        'Сотувлар орқали корхонага кирган умумий сумма. Қанча юқори бўлса, савдо ҳажми шунча яхши.'
    },
    {
      metric: 'Маҳсулот Таннархи (COGS)',
      p1: p1C,
      p2: p2C,
      diff: cogsDiff,
      growth: cogsGrowth,
      status: cogsGrowth <= 0 ? 'positive' : 'negative',
      desc: 'Сотилган товарларнинг асл харид ва тайёрлаш қиймати',
      tooltip:
        'Маҳсулотларни омборга олиб келиш ёки ишлаб чиқариш учун сарфланган тўғридан-тўғри харажат.'
    },
    {
      metric: 'Доимий Ишчилар Маоши (Staff Salaries)',
      p1: p1Staff,
      p2: p2Staff,
      diff: parseFloat((p1Staff - p2Staff).toFixed(2)),
      growth: parseFloat((((p1Staff - p2Staff) / p2Staff) * 100).toFixed(1)),
      status: 'neutral',
      desc: 'Доимий штатдаги ходимларнинг белгиланган тариф ойликлари',
      tooltip: 'Ҳар ой ходимларга тўланадиган қатъий белгиланган асосий ойлик маошлар йиғиндиси.'
    },
    {
      metric: 'Қисқа Муддатли Ишчилар (Piece-rate / Выработка)',
      p1: p1Short,
      p2: p2Short,
      diff: parseFloat((p1Short - p2Short).toFixed(2)),
      growth: parseFloat((((p1Short - p2Short) / p2Short) * 100).toFixed(1)),
      status: 'neutral',
      desc: 'Ҳосил ёки бажарилган иш ҳажми бўйича тўланган иш ҳақи',
      tooltip:
        'Вақтинча ёки донабай (выработка) ишчилар бажарган ҳажмларига қараб олган тўловлар.'
    },
    {
      metric: 'Жами Иш Ҳақи Харажатлари (Total Payroll)',
      p1: p1Pay,
      p2: p2Pay,
      diff: payrollDiff,
      growth: payrollGrowth,
      status: payrollGrowth <= 0 ? 'positive' : 'negative',
      desc: 'Компаниянинг барча ойлик тўловлари йиғиндиси',
      tooltip:
        'Доимий ойликлар ва қўшимча иш ҳажми учун тўланган барча меҳнат харажатлари суммаси.'
    },
    {
      metric: `${t('erp.realNetProfit')} (Real Net Profit)`,
      p1: p1Prof,
      p2: p2Prof,
      diff: profitDiff,
      growth: profitGrowth,
      status: profitGrowth >= 0 ? 'positive' : 'negative',
      desc: 'Таннарх ва барча ойликлар чегирилган тоза фойда',
      tooltip: 'Компаниянинг барча харажатларидан кейин тоза чўнтагига қолган ҳақиқий даромад.'
    },
    {
      metric: 'Рентабеллик Маржаси (Profit Margin %)',
      p1: p1Marg,
      p2: p2Marg,
      diff: marginDiff,
      growth: marginDiff,
      isPercentage: true,
      status: marginDiff >= 0 ? 'positive' : 'negative',
      desc: 'Соф фойданинг умумий тушумдаги фоиз улуши',
      tooltip:
        'Ҳар $100 долларлик савдодан компанияга неча доллар соф фойда қолаётганини кўрсатувчи самарадорлик индекси.'
    }
  ]"""

new_comp_table = """  // 5. Update Comparison Table Data with reactive i18n
  comparisonTable.value = [
    {
      metric: t('analysis.metricGrossRevenue'),
      p1: p1Rev,
      p2: p2Rev,
      diff: revDiff,
      growth: revGrowth,
      status: revGrowth >= 0 ? 'positive' : 'negative',
      desc: t('analysis.metricGrossRevenueDesc'),
      tooltip: t('analysis.metricGrossRevenueTip')
    },
    {
      metric: t('analysis.metricCogs'),
      p1: p1C,
      p2: p2C,
      diff: cogsDiff,
      growth: cogsGrowth,
      status: cogsGrowth <= 0 ? 'positive' : 'negative',
      desc: t('analysis.metricCogsDesc'),
      tooltip: t('analysis.metricCogsTip')
    },
    {
      metric: t('analysis.metricStaffSalaries'),
      p1: p1Staff,
      p2: p2Staff,
      diff: parseFloat((p1Staff - p2Staff).toFixed(2)),
      growth: parseFloat((((p1Staff - p2Staff) / p2Staff) * 100).toFixed(1)),
      status: 'neutral',
      desc: t('analysis.metricStaffSalariesDesc'),
      tooltip: t('analysis.metricStaffSalariesTip')
    },
    {
      metric: t('analysis.metricPiecework'),
      p1: p1Short,
      p2: p2Short,
      diff: parseFloat((p1Short - p2Short).toFixed(2)),
      growth: parseFloat((((p1Short - p2Short) / p2Short) * 100).toFixed(1)),
      status: 'neutral',
      desc: t('analysis.metricPieceworkDesc'),
      tooltip: t('analysis.metricPieceworkTip')
    },
    {
      metric: t('analysis.metricTotalPayroll'),
      p1: p1Pay,
      p2: p2Pay,
      diff: payrollDiff,
      growth: payrollGrowth,
      status: payrollGrowth <= 0 ? 'positive' : 'negative',
      desc: t('analysis.metricTotalPayrollDesc'),
      tooltip: t('analysis.metricTotalPayrollTip')
    },
    {
      metric: t('analysis.metricRealNetProfit'),
      p1: p1Prof,
      p2: p2Prof,
      diff: profitDiff,
      growth: profitGrowth,
      status: profitGrowth >= 0 ? 'positive' : 'negative',
      desc: t('analysis.metricRealNetProfitDesc'),
      tooltip: t('analysis.metricRealNetProfitTip')
    },
    {
      metric: t('analysis.metricProfitMargin'),
      p1: p1Marg,
      p2: p2Marg,
      diff: marginDiff,
      growth: marginDiff,
      isPercentage: true,
      status: marginDiff >= 0 ? 'positive' : 'negative',
      desc: t('analysis.metricProfitMarginDesc'),
      tooltip: t('analysis.metricProfitMarginTip')
    }
  ]"""
if old_comp_table in content:
    content = content.replace(old_comp_table, new_comp_table)
    print("✓ Replaced comparison table logic")

# Confirm messages in script
content = content.replace("ElMessage.warning('Илтимос, ҳисобот ойини танланг!')", "ElMessage.warning(t('analysis.selectMonthWarn'))")
content = content.replace("title: 'Ойлик Ҳисоботни Муҳрлаш'", "title: t('analysis.confirmCloseTitle')")
content = content.replace("confirmButtonText: 'Ҳа, Муҳрлаш ва Сақлаш'", "confirmButtonText: t('analysis.confirmCloseBtn')")
content = content.replace("cancelButtonText: 'Бекор қилиш'", "cancelButtonText: t('analysis.cancelBtn')")
content = content.replace("title: 'Тарихни ўчириш'", "title: t('analysis.confirmDeleteTitle')")
content = content.replace("confirmButtonText: 'Ўчириш'", "confirmButtonText: t('analysis.deleteBtn')")

# Template replacements:
TEMPLATE_REPLACEMENTS = [
    # Top mode tooltips
    ('content="Компаниянинг умумий молиявий оқимлари, ойлик динамика ва категориялар бўйича рентабеллик кўриниши"',
     ':content="t(\'analysis.tipStandardAnalysis\') || t(\'analysis.standardAnalysis\')"'),
    ('content="Ҳар бир ойни расмий ёпиш, соф фойдани музлатиш, ўша ойдаги барча савдо чеклари ва архивланган ҳисоботлар"',
     ':content="t(\'analysis.tipMonthlyClosing\') || t(\'analysis.monthlyClosing\')"'),
    ('content="Икки давр (жорий ой ва ўтган ой, ёки чораклар) ўртасидаги даромад, харажат, ойликлар ва соф фойданинг мутлақ ва фоиз ўзгариши (Делта) таҳлили"',
     ':content="t(\'analysis.tipComparePeriods\') || t(\'analysis.comparePeriods\')"'),
    ('content="Барча савдо, ходимлар, омбор ва молиявий маълумотларни базадан қайта юклаш"',
     ':content="t(\'analysis.tipRefresh\') || t(\'common.refresh\')"'),
    ('content="Охирги 6 ой давомида тушум, таннарх, ойликлар ва ҳақиқий соф фойданинг ўзгариш чизиқлари"',
     ':content="t(\'analysis.tipFinancialDynamics\') || t(\'analysis.financialDynamics\')"'),
    ('content="Жами харажатларнинг қайси қисми маҳсулот таннархига, қайси қисми иш ҳақига тўғри келишининг фоиз тақсимоти"',
     ':content="t(\'analysis.tipExpenseStructure\') || t(\'analysis.expenseStructure\')"'),
    ('content="Маҳсулот тоифалари (категориялар) бўйича жами савдо суммаси ва улардан қолган соф фойда"',
     ':content="t(\'analysis.tipCategoryProfitability\') || t(\'analysis.categoryProfitability\')"'),
    ('content="Ҳар бир ойнинг тушуми, таннархи, ойлик харажатлари, жами харажат ва ҳисобланган рентабеллик фоизи"',
     ':content="t(\'analysis.tipMonthlyFinancialTable\') || t(\'erp.monthlyFinancialTable\')"'),
     
    # Monthly close top
    ("""                <p class="text-13px text-gray-500 dark:text-gray-400 mt-2px">
                  Танланган ой бўйича тушум, харажатлар, соф фойда ва барча амалга оширилган савдо
                  битимлари (чеклар) таҳлили.
                </p>""",
     """                <p class="text-13px text-gray-500 dark:text-gray-400 mt-2px">
                  {{ t('erp.monthlyCloseReportSubtitle') }}
                </p>"""),
    ('content="Қайси ойнинг молиявий ҳисоботини кўриш ёки ёпишни хоҳласангиз, шу ойни танланг"',
     ':content="t(\'analysis.tipSelectMonth\')"'),
    ("<span>{{\n                  isSelectedMonthAlreadyClosed\n                    ? 'Қайта Ҳисоблаш & Янгилаш'\n                    : 'Ушбу Ойни Муҳрлаш & Сақлаш'\n                }}</span>",
     "<span>{{ isSelectedMonthAlreadyClosed ? t('erp.recalcAndUpdate') : t('erp.sealAndArchive') }}</span>"),
    ("{{\n                isSelectedMonthAlreadyClosed\n                  ? `${closeMonthInput} ойи расмий ёпилган ва архивга муҳрланган.`\n                  : `${closeMonthInput} ойи очиқ (Ҳали якуний муҳрланмаган).`\n              }}",
     "{{ isSelectedMonthAlreadyClosed ? `${closeMonthInput} ${t('erp.monthSealedNotice')}` : `${closeMonthInput} ${t('erp.monthOpenNotice')}` }}"),
    ("Муҳрланган сана: <b>{{ existingSnapshotForSelectedMonth.created_at }}</b> (Масъул:\n            {{ existingSnapshotForSelectedMonth.closed_by || 'admin' }})",
     "{{ t('analysis.sealedDateLabel') }} <b>{{ existingSnapshotForSelectedMonth.created_at }}</b> ({{ t('analysis.responsibleLabel') }} {{ existingSnapshotForSelectedMonth.closed_by || 'admin' }})"),
     
    # Monthly close 4 KPI cards
    ('content="Танланган ойда амалга оширилган барча савдо чекларидан тушган умумий ялпи сумма"',
     ':content="t(\'analysis.tipGrossRevenueCard\')"'),
    ('<span class="stat-subtitle">ЖАМИ ТУШУМ (САВДО)</span>',
     '<span class="stat-subtitle">{{ t(\'analysis.grossRevenueSavdoUpper\') }}</span>'),
    ('content="Сотилган барча товарларнинг асл харид ёки ишлаб чиқариш таннархи (COGS)"',
     ':content="t(\'analysis.tipCogsCard\')"'),
    ('<span class="stat-subtitle">МАҲСУЛОТ ТАННАРХИ (COGS)</span>',
     '<span class="stat-subtitle">{{ t(\'analysis.cogsUpper\') }}</span>'),
    ("""                <span
                  class="stat-subtag bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
                >
                  Тушумнинг ~{{
                    closeMonthPreview.revenue > 0
                      ? Math.round((closeMonthPreview.cogs / closeMonthPreview.revenue) * 100)
                      : 62
                  }}% қисми
                </span>""",
     """                <span
                  class="stat-subtag bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
                >
                  {{ t('analysis.revenueShare', { percent: closeMonthPreview.revenue > 0 ? Math.round((closeMonthPreview.cogs / closeMonthPreview.revenue) * 100) : 62 }) }}
                </span>"""),
    ('content="Ходимларга тўланадиган доимий тариф ойликлари ва қисқа муддатли (выработка) иш ҳажми тўловлари суммаси"',
     ':content="t(\'analysis.tipPayrollCard\')"'),
    ('<span class="stat-subtitle">ИШ ҲАҚИ ВА АВАНСЛАР</span>',
     '<span class="stat-subtitle">{{ t(\'analysis.payrollAdvancesUpper\') }}</span>'),
    ("Доимий: ${{ formatMoney(closeMonthPreview.staffSalaries) }}",
     "{{ t('analysis.permanentSalariesLabel') }} ${{ formatMoney(closeMonthPreview.staffSalaries) }}"),
    (">+ Выработка: ${{ formatMoney(closeMonthPreview.shortTerm) }}<",
     ">{{ t('analysis.pieceworkLabel') }} ${{ formatMoney(closeMonthPreview.shortTerm) }}<"),
    ('content="Барча маҳсулот таннархи ва ходимлар иш ҳақи харажатлари тўлиқ чегирилгандан кейин қолган соф фойда"',
     ':content="t(\'analysis.tipNetProfitCard\')"'),
    ('<span class="stat-subtitle text-emerald-800 dark:text-emerald-300 font-extrabold"\n                    >ҲАҚИҚИЙ СОФ ФОЙДА</span\n                  >',
     '<span class="stat-subtitle text-emerald-800 dark:text-emerald-300 font-extrabold"\n                    >{{ t(\'analysis.realNetProfitUpper\') }}</span\n                  >'),
     
    # Donut & Timeline
    ('content="Ушбу ойда қилинган ҳар бир $100 доллар даромаднинг таннарх, ойликлар ва соф фойдага тақсимланиш ҳалқаси"',
     ':content="t(\'analysis.tipDistributionRing\')"'),
    ('<div class="center-title">СОФ ФОЙДА</div>',
     '<div class="center-title">{{ t(\'analysis.netProfitUpper\') }}</div>'),
    ("{{ closeMonthPreview.margin }}% Маржа",
     "{{ closeMonthPreview.margin }}% {{ t('analysis.marginText') }}"),
    (">Выработка:<",
     ">{{ t('erp.pieceworkSalary') }}:<"),
    (">Соф Фойда:<",
     ">{{ t('erp.realNetProfit') }}:<"),
    ('content="Охирги 6 ой давомида тушум, харажатлар ва соф фойданинг узлуксиз ўсиш эгри чизиқлари"',
     ':content="t(\'analysis.tipEvolutionTimeline\')"'),
    ('>Ҳар ой бўйича узлуксиз ўсиш эгри чизиғи<',
     '>{{ t(\'analysis.splineSubtitle\') }}<'),
     
    # Bottom Table controls
    ('content="Танланган ойда рўй берган барча савдо операциялари ва чеклар рўйхати"',
     ':content="t(\'analysis.tipSalesList\')"'),
    ('Танланган ({{ closeMonthInput }}) Ойи Савдолари ({{ filteredMonthlySales.length }}\n                  {{ t(\'erp.dealsCountSuffix\') }})',
     '{{ t(\'analysis.monthlySalesTab\', { month: closeMonthInput, count: filteredMonthlySales.length }) }}'),
    ('content="Олдинги ёпилган ва муҳрланган барча ойларнинг расмий архив жадваллари"',
     ':content="t(\'analysis.tipArchiveList\')"'),
    ('Архивланган Ойлар Тарихи ({{ savedSnapshots.length }} та ой)',
     '{{ t(\'analysis.archivedMonthsTab\', { count: savedSnapshots.length }) }}'),
    ('content="Танланган ой бўйича барча чекларнинг умумий йиғиндиси"',
     ':content="t(\'analysis.tipTotalSalesSummary\')"'),
    ('>Жами Савдо:<',
     '>{{ t(\'analysis.totalSalesLabel\') }}<'),
    ('content="Мижозлар томонидан амалда тўлаб берилган сумма"',
     ':content="t(\'analysis.tipPaidSummary\')"'),
    ('>Тўланган:<',
     '>{{ t(\'analysis.paidLabel\') }}<'),
    ('content="Насия / қарзга олинган товарлар суммаси"',
     ':content="t(\'analysis.tipDebtSummary\')"'),
    ('>Қарз:<',
     '>{{ t(\'analysis.debtLabel\') }}<'),
    ('content="Савдо маълумотларини янгилаш"',
     ':content="t(\'analysis.tipRefresh\')"'),
    ('> Янгилаш',
     '> {{ t(\'common.refresh\') }}'),
    ('content="Архивдаги барча ойларни қайта юклаш"',
     ':content="t(\'analysis.tipRefresh\')"'),
    ('content="Чек рақами, мижоз исми, телефон рақами ёки кассир бўйича қидириш"',
     ':content="t(\'analysis.tipSearchSales\')"'),
    ('placeholder="Чек рақами, мижоз исми ёки кассир..."',
     ':placeholder="t(\'analysis.searchPlaceholder\')"'),
    ('content="Тўлов тури бўйича фильтрлаш (Нақд, Карта, Насия, Ўтказма)"',
     ':content="t(\'analysis.tipFilterPayment\')"'),
    ('placeholder="Тўлов усули"',
     ':placeholder="t(\'analysis.paymentMethodPlaceholder\')"'),
    ('label="Барча тўлов усуллари"',
     ':label="t(\'analysis.allPaymentMethods\')"'),
    ('label="Нақд пул"',
     ':label="t(\'analysis.cashPayment\')"'),
    ('label="Пластик карта"',
     ':label="t(\'analysis.cardPayment\')"'),
     
    # Empty states & table columns
    ('>Ушбу ой учун савдо чеклари топилмади<',
     '>{{ t(\'analysis.noSalesFound\') }}<'),
    ('>Қидирув параметрларини ўзгартиринг ёки янги сотув амалга оширинг.<',
     '>{{ t(\'analysis.noSalesFoundSub\') }}<'),
    ('content="Ноёб транзакция / чек коди"',
     ':content="t(\'analysis.tipReceiptCode\')"'),
    ('label="Мижоз (Харидор)"',
     ':label="t(\'analysis.customerLabel\')"'),
    ("{{ row.customer_name || 'Умумий харидор (Walk-in)' }}",
     "{{ row.customer_name || t('analysis.walkInCustomer') }}"),
    ('label="Тўлов Усули"',
     ':label="t(\'analysis.paymentMethodLabel\')"'),
    ('\n                  Нақд\n',
     '\n                  {{ t(\'analysis.cashPayment\') }}\n'),
    ('\n                  Карта\n',
     '\n                  {{ t(\'analysis.cardPayment\') }}\n'),
    ('\n                  Насия\n',
     '\n                  {{ t(\'erp.debt\') }}\n'),
    ('\n                  Ўтказма\n',
     '\n                  {{ t(\'erp.bankTransfer\') }}\n'),
    ("|| 'Нақд'",
     "|| t('analysis.cashPayment')"),
    ('label="Маҳсулотлар"',
     ':label="t(\'analysis.productsCountLabel\')"'),
    ('{{ (row.items && row.items.length) || row.total_items || 1 }} хил',
     '{{ (row.items && row.items.length) || row.total_items || 1 }} {{ t(\'erp.typesCount\') }}'),
    ('label="Тўланган ($)"',
     ':label="t(\'analysis.paidAmountDollarLabel\')"'),
    ('label="Қарз ($)"',
     ':label="t(\'analysis.debtAmountDollarLabel\')"'),
    ('label="Вақти"',
     ':label="t(\'analysis.timeLabel\')"'),
    ('content="Чек ичидаги барча товарлар рўйхати, нархлари ва миқдорини кўриш"',
     ':content="t(\'analysis.tipViewReceiptDetail\')"'),
    ('> Чекни кўриш',
     '> {{ t(\'analysis.viewReceipt\') }}'),
    ('>Ҳали ёпилган ойлик молиявий ҳисоботлар мавжуд эмас<',
     '>{{ t(\'analysis.noArchivedMonths\') }}<'),
    ('>Юқоридаги "Ушбу Ойни Муҳрлаш & Сақлаш" тугмаси орқали ўтган ойларни архивга\n              сақлашингиз мумкин.<',
     '>{{ t(\'analysis.noArchivedMonthsSub\') }}<'),
    ('label="Битимлар"',
     ':label="t(\'analysis.dealsLabel\')"'),
    ('{{ row.sales_count }} та савдо',
     '{{ row.sales_count }} {{ t(\'erp.dealsCountSuffix\') }}'),
    ('label="Рентабеллик"',
     ':label="t(\'analysis.profitabilityLabel\')"'),
    ('> Муҳрланган',
     '> {{ t(\'analysis.sealedStatus\') }}'),
    ('label="Муҳрланган сана"',
     ':label="t(\'analysis.sealedDateCol\')"'),
    ('content="Ушбу ойнинг расмий муҳрланган сертификатини кўриш"',
     ':content="t(\'analysis.tipViewArchiveCert\')"'),
    ('> Кўриш',
     '> {{ t(\'analysis.viewText\') }}'),
    ('content="Ушбу ойлик архив ҳисоботини базадан ўчириш"',
     ':content="t(\'analysis.tipDeleteArchiveReport\')"'),
     
    # Receipt modal
    (':title="`Савдо Чеки: ${selectedSaleDetail?.receipt_number || selectedSaleDetail?.id || \'\'}`"',
     ':title="t(\'analysis.receiptTitle\', { number: selectedSaleDetail?.receipt_number || selectedSaleDetail?.id || \'\' })"'),
    ('>Харидор:<',
     '>{{ t(\'analysis.buyerLabel\') }}<'),
    ('>Сана ва Кассир:<',
     '>{{ t(\'analysis.dateAndCashier\') }}<'),
    ('label="Нархи ($)"',
     ':label="t(\'analysis.priceDollar\')"'),
    ('label="Жами ($)"',
     ':label="t(\'analysis.totalDollar\')"'),
    ('>ЖАМИ ЧЕК СУММАСИ:<',
     '>{{ t(\'analysis.totalReceiptSum\') }}<'),
     
    # Archive snapshot dialog
    (':title="`${selectedSnapshotDetail?.period_month} Ойи Расмий Молиявий Архив Ҳисоботи`"',
     ':title="t(\'analysis.officialArchiveReportTitle\', { month: selectedSnapshotDetail?.period_month })"'),
    ('>Ҳисобот Даври:<',
     '>{{ t(\'analysis.reportPeriod\') }}<'),
    ('{{ selectedSnapshotDetail.period_month }} Ойи',
     '{{ selectedSnapshotDetail.period_month }} {{ t(\'analysis.monthlyClosing\') }}'),
    ('>Сотувлар сони:',
     '>{{ t(\'analysis.dealsCountLabel\') }}'),
    ('> РАСМИЙ МУҲРЛАНГАН',
     '> {{ t(\'analysis.officiallySealedBadge\') }}'),
    ('>Муҳрланди:',
     '>{{ t(\'analysis.sealedTimeLabel\') }}'),
    ('>1. Жами Савдо & Тушум (Gross Revenue):<',
     '>{{ t(\'analysis.line1Revenue\') }}<'),
    ('>2. Маҳсулот Таннархи (COGS):<',
     '>{{ t(\'analysis.line2Cogs\') }}<'),
    ('>3. Доимий Ишчилар Маоши ва Аванслар:<',
     '>{{ t(\'analysis.line3Staff\') }}<'),
    ('>4. Қисқа Муддатли Ишчилар (Выработка):<',
     '>{{ t(\'analysis.line4ShortTerm\') }}<'),
    ('>ЖАМИ ХАРАЖАТЛАР (TOTAL EXPENSES):<',
     '>{{ t(\'analysis.totalExpensesUpper\') }}<'),
    ('>ҲАҚИҚИЙ СОФ ФОЙДА:<',
     '>{{ t(\'analysis.realNetProfitUpper\') }}:<'),
    ('* Ушбу маълумотлар архивда музлатилган бўлиб, ўзгаришсиз сақланади. (Масъул:\n            {{ selectedSnapshotDetail.closed_by || \'admin\' }})',
     '{{ t(\'analysis.archiveNotice\', { user: selectedSnapshotDetail.closed_by || \'admin\' }) }}'),
     
    # Compare view
    ('>Таққослаш Тури:<',
     '>{{ t(\'analysis.compareType\') }}<'),
    ('content="Ойма-ой (Month-over-Month): Ушбу ойни ўтган ой билан таққослаш (Август vs Июл)"',
     ':content="t(\'analysis.tipMoM\')"'),
    ('>Ойма-ой (MoM)<',
     '>{{ t(\'analysis.compareMoM\') }}<'),
    ('content="Чоракма-чорак (Quarter-over-Quarter): Жорий 3 ойлик чоракни ўтган чорак билан таққослаш"',
     ':content="t(\'analysis.tipQoQ\')"'),
    ('>Чоракма-чорак (QoQ)<',
     '>{{ t(\'analysis.compareQoQ\') }}<'),
    ('content="Охирги 30 кунлик фаолиятни ундан олдинги 30 кунлик давр билан солиштириш"',
     ':content="t(\'analysis.tipLast30\')"'),
    ('>30 Кунлик<',
     '>{{ t(\'analysis.compareLast30\') }}<'),
    ('content="Йиллик (Year-over-Year): Бу йилги натижаларни ўтган йилги худди шу давр билан таққослаш"',
     ':content="t(\'analysis.tipYoY\')"'),
    ('>Йиллик (YoY)<',
     '>{{ t(\'analysis.compareYoY\') }}<'),
    ('content="Ихтиёрий 2 та сана оралиғини ўзингиз танлаб таққосланг"',
     ':content="t(\'analysis.tipCustom\')"'),
    ('>Махсус Сана<',
     '>{{ t(\'analysis.compareCustom\') }}<'),
    ('>1-Давр:<',
     '>{{ t(\'analysis.period1\') }}:<'),
    ('start-placeholder="Бошланиш"',
     ':start-placeholder="t(\'analysis.startPlaceholder\')"'),
    ('end-placeholder="Тугаш"',
     ':end-placeholder="t(\'analysis.endPlaceholder\')"'),
    ('>2-Давр:<',
     '>{{ t(\'analysis.period2\') }}:<'),
    ('content="1-Давр ва 2-Даврдаги барча сотувлардан тушган умумий тушум фарқи (Делта). Мусбат бўлса савдо ўсганини билдиради."',
     ':content="t(\'analysis.tipRevDiff\')"'),
    ('<div class="kpi-title">Жами Тушум Ўсиши</div>',
     '<div class="kpi-title">{{ t(\'analysis.revenueGrowth\') }}</div>'),
    ('>1-Давр: <b>${{ formatMoney(comparisonData.p1Revenue) }}</b><',
     '>{{ t(\'analysis.period1\') }}: <b>${{ formatMoney(comparisonData.p1Revenue) }}</b><'),
    ('content="Сотилган товарлар таннархининг давлар орасидаги фарқи. Товар таннархи ўсиши ёки тежалганини кўрсатади."',
     ':content="t(\'analysis.tipCogsDiff\')"'),
    ('<div class="kpi-title">Таннарх Фарқи (COGS)</div>',
     '<div class="kpi-title">{{ t(\'analysis.cogsDiff\') }}</div>'),
    ('>1-Давр: <b>${{ formatMoney(comparisonData.p1COGS) }}</b><',
     '>{{ t(\'analysis.period1\') }}: <b>${{ formatMoney(comparisonData.p1COGS) }}</b><'),
    ('content="Ходимларнинг барча ойлик маошлари ва қўшимча тўловларининг давлар орасидаги ўзгариши."',
     ':content="t(\'analysis.tipPayrollDiff\')"'),
    ('<div class="kpi-title">Иш Ҳақи Фарқи (Payroll)</div>',
     '<div class="kpi-title">{{ t(\'analysis.payrollDiff\') }}</div>'),
    ('>1-Давр: <b>${{ formatMoney(comparisonData.p1Payroll) }}</b><',
     '>{{ t(\'analysis.period1\') }}: <b>${{ formatMoney(comparisonData.p1Payroll) }}</b><'),
    ('content="Барча таннарх ва ойликлар чегирилгандан кейин қолган соф даромаднинг ўсиши ёки камайиши (Ҳақиқий бизнес натижаси)."',
     ':content="t(\'analysis.tipProfitDiff\')"'),
    ('<div class="kpi-title text-emerald-700 dark:text-emerald-300 font-extrabold"\n                >{{ t(\'erp.realNetProfit\') }} Ўзгариши</div\n              >',
     '<div class="kpi-title text-emerald-700 dark:text-emerald-300 font-extrabold"\n                >{{ t(\'analysis.netProfitChange\') }}</div\n              >'),
    ('>1-Давр: <b>${{ formatMoney(comparisonData.p1Profit) }}</b> ({{',
     '>{{ t(\'analysis.period1\') }}: <b>${{ formatMoney(comparisonData.p1Profit) }}</b> ({{'),
    ('content="1-Давр ва 2-Даврнинг ҳар бир асосий кўрсаткичини ёнма-ён солиштириб берувчи устунли график"',
     ':content="t(\'analysis.tipComparisonBar\')"'),
    ('<span class="header-title cursor-help"\n                  >{{ period1Label }} vs {{ period2Label }} Таққослаш Графикаси</span\n                >',
     '<span class="header-title cursor-help"\n                  >{{ period1Label }} vs {{ period2Label }} {{ t(\'analysis.comparisonChart\') }}</span\n                >'),
    ('content="1-Даврда топилган умумий даромад қайси йўналишларга (таннарх, ойликлар, соф фойда) қандай фоизда тақсимланганини кўрсатади"',
     ':content="t(\'analysis.tipRevenueStructure\')"'),
    ('<span class="header-title cursor-help">1-Давр Даромад Структураси</span>',
     '<span class="header-title cursor-help">{{ t(\'analysis.revenueStructure\') }}</span>'),
    ('content="Ҳар бир молиявий кўрсаткичнинг 1-давр ва 2-давридаги аниқ суммалари, уларнинг айирмаси (Делта) ва фоиздаги ўзгариш суръати"',
     ':content="t(\'analysis.tipDeltaTable\')"'),
    ('<span class="header-title cursor-help"\n                >Кўрсаткичларнинг Тўлиқ Делта ва Фоиз Ўзгариши Жадвали</span\n              >',
     '<span class="header-title cursor-help"\n                >{{ t(\'analysis.deltaTableTitle\') }}</span\n              >'),
    ('label="Молиявий Кўрсаткич"',
     ':label="t(\'analysis.financialMetric\')"'),
    ('content="1-Давр (асосий давр) бўйича ҳисобланган сумма"',
     ':content="t(\'analysis.tipP1Value\')"'),
    ('content="2-Давр (таққосланаётган давр) бўйича ҳисобланган сумма"',
     ':content="t(\'analysis.tipP2Value\')"'),
    ('label="Мутлақ Фарқ (Делта)"',
     ':label="t(\'analysis.absoluteDiff\')"'),
    ('content="Сумма ҳисобидаги мутлақ фарқ: 1-Давр - 2-Давр"',
     ':content="t(\'analysis.tipDiffValue\')"'),
    ('label="Ўсиш Суръати (%)"',
     ':label="t(\'analysis.growthRate\')"'),
    ('content="Олдинги даврга нисбатан фоиз ҳисобидаги ўсиш (+) ёки пасайиш (-) даражаси"',
     ':content="t(\'analysis.tipGrowthValue\')"'),
]

t_count = 0
for old, new in TEMPLATE_REPLACEMENTS:
    if old in content:
        content = content.replace(old, new)
        t_count += 1
        print(f"  ✓ [{t_count}] Replaced template string: {old[:50]}...")
    else:
        print(f"  ⚠ Not found in template: {old[:50]}...")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total template replacements applied: {t_count}")
