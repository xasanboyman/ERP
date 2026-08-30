import re
from generate_cr_locale import convert_uz_to_cr

def expand_locales():
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()

    new_analysis_keys = """    standardAnalysis: 'Standart Moliyaviy Tahlil',
    monthlyClosing: 'Oylik Yopilish & Tarixiy Arxiv',
    comparePeriods: 'Davrlarni Taqqoslash (Delta)',
    grossRevenue: 'Jami Tushum (Gross Revenue)',
    salesAndTurnover: 'Savdolar va Aylanma',
    cogs: 'Mahsulot Tannarxi (COGS)',
    totalPayroll: 'Jami Ish Haqi Xarajati',
    realNetProfit: 'Haqiqiy Sof Foyda',
    permanentStaff: 'Doimiy',
    shortTerm: 'Yollanma',
    afterSalaries: 'Barcha oylik va xarajatlardan keyin',
    financialDynamics: 'Oylik Tushum, Xarajatlar va Haqiqiy Sof Foyda Dinamikasi',
    expenseStructure: 'Daromad va Xarajatlar Strukturasi',
    categoryProfitability: 'Kategoriyalar Bo‘yicha Tushum va Sof Foyda',
    last6Months: 'Oxirgi 6 oy',
    yearly: 'Yillik',
    revenueShare: 'Tushumning ~{percent}% qismi',
    permanentSalaries: 'Doimiy Xodimlar Maoshi',
    shortTermWorkers: 'Qisqa Muddatli Ishchilar',
    totalSalesValue: 'Jami Savdo Qiymati',
    netProfitShare: 'Sof Foyda Qismi',
"""

    if 'standardAnalysis' not in uz_text:
        uz_text = uz_text.replace("analysis: {\n", "analysis: {\n" + new_analysis_keys)

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)

    # Also update en.ts
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    en_analysis_keys = """    standardAnalysis: 'Standard Financial Analysis',
    monthlyClosing: 'Monthly Closing & Historical Archive',
    comparePeriods: 'Compare Periods (Delta)',
    grossRevenue: 'Gross Revenue',
    salesAndTurnover: 'Sales and Turnover',
    cogs: 'Cost of Goods Sold (COGS)',
    totalPayroll: 'Total Payroll Expenses',
    realNetProfit: 'Real Net Profit',
    permanentStaff: 'Permanent',
    shortTerm: 'Contractors',
    afterSalaries: 'After all payroll and expenses',
    financialDynamics: 'Monthly Revenue, Expenses and Real Net Profit Dynamics',
    expenseStructure: 'Revenue and Expense Structure',
    categoryProfitability: 'Revenue and Profit by Category',
    last6Months: 'Last 6 months',
    yearly: 'Yearly',
    revenueShare: '~{percent}% of gross revenue',
    permanentSalaries: 'Permanent Staff Salaries',
    shortTermWorkers: 'Short-term Workers',
    totalSalesValue: 'Total Sales Value',
    netProfitShare: 'Net Profit Share',
"""
    if 'standardAnalysis' not in en_text:
        en_text = en_text.replace("analysis: {\n", "analysis: {\n" + en_analysis_keys)

    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_text)

    # Re-generate cr.ts from updated uz.ts
    convert_uz_to_cr()
    print("Locales expanded and cr.ts regenerated successfully")

if __name__ == '__main__':
    expand_locales()
