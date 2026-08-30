import os
import re
import json

NEW_KEYS = [
    # Debtors
    ("initialDebt", "Dastlabki Qarz", "Initial Debt"),
    ("deals", "Bitim", "Deals"),
    ("repay", "Qaytarish", "Repay"),
    ("history", "Tarix", "History"),
    ("activeDebtors", "Faol Qarzdorlar", "Active Debtors"),
    ("totalCustomers", "Jami Mijozlar", "Total Customers"),
    ("allStatuses", "Barcha holatlar", "All statuses"),
    ("activeDebts", "Faol Qarzlar", "Active Debts"),
    ("settledDebts", "Qarzini Uzganlar", "Settled Debts"),
    ("exportExcel", "Excelga Eksport", "Export to Excel"),
    ("repayDebt", "Qarz Qaytarish", "Debt Repayment"),
    ("selectOrEnterCustomer", "Mijoz tanlang yoki kiriting", "Select or enter customer"),
    ("repayAmountDollar", "Qaytarilayotgan Summa ($)", "Repayment Amount ($)"),
    ("paymentMethodLabel", "To'lov Usuli", "Payment Method"),
    ("afterPaymentRemaining", "To'lovdan keyin qoladi:", "Remaining after payment:"),
    ("acceptPayment", "Qabul Qilish", "Accept Payment"),
    ("settledBadge", "✓ Uzilgan", "✓ Settled"),
    ("paidPct", "to'langan", "paid"),
    ("searchNameOrPhone", "Ismi yoki telefon...", "Name or phone..."),
    ("debtorCustomer", "Qarzdor Mijoz", "Debtor Customer"),
    ("existingDebt", "Mavjud Nasiya Qarz", "Existing Debt"),
    ("enterAmount", "Summani kiriting...", "Enter amount..."),
    ("additionalRemark", "Qo'shimcha izoh...", "Additional remarks..."),
    ("repayModalTitle", "Qarz Qaytarish — To'lov Qabul Qilish", "Debt Repayment — Receive Payment"),
    ("transferPayment", "🏦 O'tkazma", "🏦 Transfer"),

    # Worker & HR
    ("workerList", "Xodimlar Ro'yxati", "Worker List"),
    ("addWorker", "Yangi Xodim Qo'shish", "Add New Worker"),
    ("workerFullName", "Xodim F.I.Sh.", "Worker Full Name"),
    ("passportNumber", "Pasport Raqami", "Passport Number"),
    ("hireDate", "Ishga Kirgan Sanasi", "Hire Date"),
    ("dailyWage", "Kunlik Maoshi", "Daily Wage"),
    ("monthlySalary", "Oylik Maoshi", "Monthly Salary"),

    # Salary
    ("calculateSalary", "Oylik Hisoblash", "Calculate Salary"),
    ("paySalary", "Oylik To'lash", "Pay Salary"),
    ("payrollMonth", "Hisob Oyi", "Payroll Month"),
    ("totalCalculated", "Jami Hisoblangan", "Total Calculated"),
    ("totalPaid", "Jami To'langan", "Total Paid"),
    ("totalBalance", "Jami Qoldiq", "Total Balance"),

    # Product
    ("productCatalog", "Mahsulotlar Katalogi", "Product Catalog"),
    ("addProduct", "Yangi Mahsulot", "New Product"),
    ("inventoryStock", "Ombor Qoldig'i", "Inventory Stock"),
    ("categoryName", "Kategoriya Nomi", "Category Name"),
    ("allCategories", "Barcha Kategoriyalar", "All Categories"),

    # Cutting & Techmap
    ("cuttingTasks", "Bichuv Vazifalari", "Cutting Tasks"),
    ("newCuttingTask", "Yangi Bichuv Topshirig'i", "New Cutting Task"),
    ("techmapList", "Texkarta Ro'yxati", "Techmap List"),
    ("createTechmap", "Texkarta Yaratish", "Create Techmap"),
]

REPLACEMENTS = [
    (r'>\s*Dastlabki Qarz\s*<', r'>{{ t("erp.initialDebt") }}<'),
    (r'label="Dastlabki Qarz"', r':label="t(\'erp.initialDebt\')"'),
    (r'label="Bitim"', r':label="t(\'erp.deals\')"'),
    (r'>\s*Faol Qarzdorlar\s*<', r'>{{ t("erp.activeDebtors") }}<'),
    (r'>\s*Jami Mijozlar\s*<', r'>{{ t("erp.totalCustomers") }}<'),
    (r'>\s*Jami Nasiya Qarz\s*<', r'>{{ t("erp.totalDebts") }}<'),
    (r'label="🔍 Barcha holatlar"', r':label="t(\'erp.allStatuses\')"'),
    (r'label="🔴 Faol Qarzlar"', r':label="t(\'erp.activeDebts\')"'),
    (r'label="✅ Qarzini Uzganlar"', r':label="t(\'erp.settledDebts\')"'),
    (r'>\s*Excelga Eksport\s*<', r'>{{ t("erp.exportExcel") }}<'),
    (r'>\s*Qarz Qaytarish\s*<', r'>{{ t("erp.repayDebt") }}<'),
    (r'>\s*Qaytarish\s*<', r'>{{ t("erp.repay") }}<'),
    (r'>\s*Tarix\s*<', r'>{{ t("erp.history") }}<'),
    (r'>\s*✓ Uzilgan\s*<', r'>{{ t("erp.settledBadge") }}<'),
    (r'placeholder="Ismi yoki telefon\.\.\."', r':placeholder="t(\'erp.searchNameOrPhone\')"'),
    (r'title="Qarz Qaytarish — To\'lov Qabul Qilish"', r':title="t(\'erp.repayModalTitle\')"'),
    (r'>\s*Qarzdor Mijoz\s*<', r'>{{ t("erp.debtorCustomer") }}<'),
    (r'>\s*Mavjud Nasiya Qarz\s*<', r'>{{ t("erp.existingDebt") }}<'),
    (r'>\s*Mijoz tanlang yoki kiriting\s*<', r'>{{ t("erp.selectOrEnterCustomer") }}<'),
    (r'>\s*Qaytarilayotgan Summa \(\$\)\s*<', r'>{{ t("erp.repayAmountDollar") }}<'),
    (r'>\s*To\'lov Usuli\s*<', r'>{{ t("erp.paymentMethodLabel") }}<'),
    (r'>\s*To\'lovdan keyin qoladi:\s*<', r'>{{ t("erp.afterPaymentRemaining") }}<'),
    (r'Qabul Qilish \(\$\{\{\s*formatMoney\(repayForm\.amount\)\s*\}\}\)', r'{{ t("erp.acceptPayment") }} (${{ formatMoney(repayForm.amount) }})'),
    (r'>\s*🏦 O\'tkazma\s*<', r'>{{ t("erp.transferPayment") }}<'),
    (r'placeholder="Summani kiriting\.\.\."', r':placeholder="t(\'erp.enterAmount\')"'),
    (r'placeholder="Qo\'shimcha izoh\.\.\."', r':placeholder="t(\'erp.additionalRemark\')"'),
    (r'>\s*Bekor\s*<', r'>{{ t("common.cancel") }}<'),
]

def run():
    print("Updating dictionary with rich debt and HR keys...")
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'
    
    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    for k, uz_v, en_v in NEW_KEYS:
        uz_entry = f"    {k}: {json.dumps(uz_v, ensure_ascii=False)},"
        en_entry = f"    {k}: {json.dumps(en_v, ensure_ascii=False)},"
        if f"{k}:" not in uz_text:
            uz_text = uz_text.replace("erp: {", "erp: {\n" + uz_entry)
        if f"{k}:" not in en_text:
            en_text = en_text.replace("erp: {", "erp: {\n" + en_entry)

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_text)

    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()

    # Vue replacements
    for root, dirs, files in os.walk('/home/xasanboy/ERP/Front/src/views'):
        for file in files:
            if file.endswith('.vue'):
                p = os.path.join(root, file)
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                orig = content
                for pat, rep in REPLACEMENTS:
                    content = re.sub(pat, rep, content)
                if content != orig:
                    if "useI18n" not in content:
                        content = re.sub(r'(<script[^>]*>)', r"\1\nimport { useI18n } from '@/hooks/web/useI18n'\nconst { t } = useI18n()", content, count=1)
                    elif "const { t } = useI18n()" not in content and "const { t," not in content:
                        content = re.sub(r'(<script[^>]*>)', r"\1\nconst { t } = useI18n()", content, count=1)

                    with open(p, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated: {file}")

if __name__ == '__main__':
    run()
