import os
import re
import json

NEW_KEYS = [
    # Tab 2 (Close / Archive)
    ("monthlyCloseReportTitle", "Oylik Moliyaviy Yopilish va Savdolar Hisoboti", "Monthly Financial Closing and Sales Report"),
    ("monthlyCloseReportSubtitle", "Tanlangan oy bo'yicha tushum, xarajatlar, sof foyda va barcha amalga oshirilgan savdo bitimlari (cheklar) tahlili.", "Analysis of revenue, expenses, net profit, and all completed sales transactions (receipts) for the selected month."),
    ("periodLabel", "Davr", "Period"),
    ("recalcAndUpdate", "Qayta Hisoblash & Yangilash", "Recalculate & Update"),
    ("sealAndArchive", "Muhrlash va Arxivga Saqlash", "Seal and Archive"),
    ("quickSelect", "Tezkor tanlash", "Quick select"),
    ("currentMonthPill", "Joriy Oy", "Current Month"),
    ("prevMonthPill", "O'tgan Oy", "Previous Month"),
    ("monthSealedNotice", "oyi rasmiy yopilgan va arxivga muhrlangan.", "month is officially closed and sealed in archive."),
    ("monthOpenNotice", "oyi hali ochiq. Istalgan vaqtda yakunlab arxivlash mumkin.", "month is still open. Can be finalized and archived at any time."),
    ("dealsCountSuffix", "ta bitim", "deals"),
    ("collectedDuringMonth", "Oy davomida yig'ilgan", "Collected during month"),
    ("materialAndGoodsValue", "Material va tovar qiymati", "Material and goods cost"),
    ("permanentSalary", "Doimiy", "Regular"),
    ("pieceworkSalary", "Vyrabotka", "Piecework"),
    ("allExpensesDeducted", "Barcha xarajatlar chegirilgan", "All expenses deducted"),
    ("financialDistributionRing", "Moliyaviy Taqsimot & Rentabellik Halqasi", "Financial Distribution & Profitability Ring"),
    ("monthlyEvolutionSpline", "Oylik Moliyaviy Rivojlanish & Arxiv Dinamikasi", "Monthly Financial Progress & Archive Dynamic"),
    ("totalSalesSavdo", "Jami Tushum (Savdo)", "Total Revenue (Sales)"),
    ("totalExpenses", "Jami Xarajatlar", "Total Expenses"),
    ("realNetProfit", "Haqiqiy Sof Foyda", "Real Net Profit"),
    ("costCogs", "Tannarx (COGS)", "Cost (COGS)"),
    ("salaries", "Oyliklar", "Salaries"),
    ("marginRatio", "Marja", "Margin"),
    ("profitability", "Rentabellik", "Profitability"),

    # Tab 3 (Comparison / Delta)
    ("periodComparisonTitle", "Ikki Davr Moliyaviy Ko'rsatkichlarini Taqqoslash", "Compare Financial Indicators of Two Periods"),
    ("periodComparisonSubtitle", "Oylar yoki davrlar orasidagi o'sish dinamikasi, rentabellik deltalari va xarajatlar o'zgarishi tahlili.", "Analysis of growth dynamics, profitability deltas, and expense fluctuations between months or periods."),
    ("basePeriod", "Baza Davri (A)", "Base Period (A)"),
    ("targetPeriod", "Taqqoslovchi Davr (B)", "Comparison Period (B)"),
    ("deltaDifference", "Farq (Delta)", "Difference (Delta)"),
    ("growthPercentage", "O'sish foizi", "Growth percentage"),
]

def run():
    print("Enriching Analysis.vue tabs 2 and 3...")
    uz_p = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_p = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_p, 'r', encoding='utf-8') as f:
        uz_t = f.read()
    with open(en_p, 'r', encoding='utf-8') as f:
        en_t = f.read()

    for k, uz_v, en_v in NEW_KEYS:
        uz_entry = f"    {k}: {json.dumps(uz_v, ensure_ascii=False)},"
        en_entry = f"    {k}: {json.dumps(en_v, ensure_ascii=False)},"
        if f"{k}:" not in uz_t:
            uz_t = uz_t.replace("erp: {", "erp: {\n" + uz_entry)
        if f"{k}:" not in en_t:
            en_t = en_t.replace("erp: {", "erp: {\n" + en_entry)

    with open(uz_p, 'w', encoding='utf-8') as f:
        f.write(uz_t)
    with open(en_p, 'w', encoding='utf-8') as f:
        f.write(en_t)

    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()

    # Update Analysis.vue
    an_p = '/home/xasanboy/ERP/Front/src/views/Dashboard/Analysis.vue'
    with open(an_p, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("Oylik Moliyaviy Yopilish va Savdolar Hisoboti", "{{ t('erp.monthlyCloseReportTitle') }}")
    content = content.replace("Tanlangan oy bo'yicha tushum, xarajatlar, sof foyda va barcha amalga oshirilgan savdo bitimlari (cheklar) tahlili.", "{{ t('erp.monthlyCloseReportSubtitle') }}")
    content = content.replace(">Qayta Hisoblash & Yangilash<", ">{{ t('erp.recalcAndUpdate') }}<")
    content = content.replace(">Muhrlash va Arxivga Saqlash<", ">{{ t('erp.sealAndArchive') }}<")
    content = content.replace("TEZKOR TANLASH:", "{{ t('erp.quickSelect') }}:")
    content = content.replace("ta bitim", "{{ t('erp.dealsCountSuffix') }}")
    content = content.replace("Oy davomida yig'ilgan", "{{ t('erp.collectedDuringMonth') }}")
    content = content.replace("Material va tovar qiymati", "{{ t('erp.materialAndGoodsValue') }}")
    content = content.replace("Barcha xarajatlar chegirilgan", "{{ t('erp.allExpensesDeducted') }}")
    content = content.replace("Moliyaviy Taqsimot & Rentabellik Halqasi", "{{ t('erp.financialDistributionRing') }}")
    content = content.replace("Oylik Moliyaviy Rivojlanish & Arxiv Dinamikasi", "{{ t('erp.monthlyEvolutionSpline') }}")
    content = content.replace("Jami Tushum (Savdo)", "{{ t('erp.totalSalesSavdo') }}")
    content = content.replace("Jami Xarajatlar", "{{ t('erp.totalExpenses') }}")
    content = content.replace("Haqiqiy Sof Foyda", "{{ t('erp.realNetProfit') }}")
    content = content.replace("Tannarx (COGS)", "{{ t('erp.costCogs') }}")
    content = content.replace("Oyliklar", "{{ t('erp.salaries') }}")
    content = content.replace("Rentabellik:", "{{ t('erp.profitability') }}:")

    with open(an_p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Analysis.vue successfully!")

if __name__ == '__main__':
    run()
