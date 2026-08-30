import os
import re
import json

NEW_KEYS = [
    # Product
    ("productTypesCount", "Ombor Mahsulot Turlari", "Product Types in Warehouse"),
    ("totalWarehouseStock", "Jami Ombordagi Soni", "Total Warehouse Stock"),
    ("totalCostValue", "Jami Tannarx Qiymati", "Total Cost Value"),
    ("totalSalesValueStat", "Jami Sotuv Qiymati", "Total Sales Value"),
    ("searchProductAdv", "Shtrix-kod, Nomi, Brend yoki MXIK izlash...", "Search barcode, name, brand or MXIK..."),
    ("allCategoriesFilter", "Barcha kategoriyalar", "All categories"),
    ("newProductEntry", "Yangi Mahsulot Kirim Qilish", "New Product Entry"),
    ("image", "Rasm", "Image"),
    ("brand", "Brend", "Brand"),
    ("mxikCode", "MXIK Kodi", "MXIK Code"),
    ("quantityInStock", "Ombordagi miqdor", "Quantity in Stock"),
    ("costPriceDollar", "Tannarxi ($)", "Cost Price ($)"),
    ("sellingPriceDollar", "Sotuv narxi ($)", "Selling Price ($)"),
    ("expirationDate", "Yaroqlilik muddati", "Expiration Date"),
    ("clickToCopy", "Nusxalash uchun bosing", "Click to copy"),
    ("others", "Boshqalar", "Others"),

    # Worker & HR
    ("activeWorkers", "Faol Xodimlar", "Active Workers"),
    ("totalMonthlyFund", "Jami Oylik Fondi", "Total Monthly Fund"),
    ("avgDailyRate", "O'rtacha Kunlik Stavka", "Avg Daily Rate"),
    ("positionsCount", "Lavozimlar Soni", "Positions Count"),
    ("addWorkerBtn", "Yangi Xodim Qo'shish", "Add New Worker"),
    ("workerSearchPlaceholder", "Xodim F.I.Sh, telefon yoki pasport...", "Worker name, phone or passport..."),

    # Salary
    ("totalPayrollFund", "Jami Oylik Fondi", "Total Payroll Fund"),
    ("paidAmountStat", "To'langan Summa", "Paid Amount"),
    ("unpaidAmountStat", "To'lanmagan Qoldiq", "Unpaid Balance"),
    ("paidWorkersCount", "Oylik Olgan Xodimlar", "Paid Workers Count"),
    ("calculatePayroll", "Oylik Hisoblash (Avtomat)", "Calculate Payroll (Auto)"),
    ("batchPaySalary", "Ommaviy Oylik To'lash", "Batch Pay Salary"),

    # Output & Timesheet
    ("dailyOutput", "Kunlik Ishlab Chiqarish", "Daily Output"),
    ("addOutput", "Ishlab Chiqarish Kiritish", "Add Production Output"),
    ("timesheetReport", "Tabel Hisoboti", "Timesheet Report"),
    ("fillTimesheet", "Tabel To'ldirish", "Fill Timesheet"),

    # Adjustment
    ("bonusPenalty", "Bonus va Jarimalar", "Bonuses and Penalties"),
    ("addAdjustment", "Bonus/Jarima Qo'shish", "Add Bonus/Penalty"),

    # Techmap & Cutting
    ("techmapTitle", "Texnologik Xarita", "Techmap"),
    ("addTechmap", "Yangi Texkarta", "New Techmap"),
    ("cuttingQueue", "Bichuv Navbati", "Cutting Queue"),
    ("addCuttingTask", "Bichuv Topshirig'i", "New Cutting Order")
]

REPLACEMENTS = [
    # Product
    (r'>\s*Ombor Mahsulot Turlari\s*<', r'>{{ t("erp.productTypesCount") }}<'),
    (r'>\s*Jami Ombordagi Soni\s*<', r'>{{ t("erp.totalWarehouseStock") }}<'),
    (r'>\s*Jami Tannarx Qiymati\s*<', r'>{{ t("erp.totalCostValue") }}<'),
    (r'>\s*Jami Sotuv Qiymati\s*<', r'>{{ t("erp.totalSalesValueStat") }}<'),
    (r'placeholder="Shtrix-kod, Nomi, Brend yoki MXIK izlash\.\.\."', r':placeholder="t(\'erp.searchProductAdv\')"'),
    (r'placeholder="Barcha kategoriyalar"', r':placeholder="t(\'erp.allCategoriesFilter\')"'),
    (r'>\s*Yangi Mahsulot Kirim Qilish\s*<', r'>{{ t("erp.newProductEntry") }}<'),
    (r'label="Rasm"', r':label="t(\'erp.image\')"'),
    (r'label="Brend"', r':label="t(\'erp.brand\')"'),
    (r'label="Mahsulot nomi"', r':label="t(\'erp.productName\')"'),
    (r'label="MXIK Kodi"', r':label="t(\'erp.mxikCode\')"'),
    (r'label="Ombordagi miqdor"', r':label="t(\'erp.quantityInStock\')"'),
    (r'label="Tannarxi \(\$\)"', r':label="t(\'erp.costPriceDollar\')"'),
    (r'label="Sotuv narxi \(\$\)"', r':label="t(\'erp.sellingPriceDollar\')"'),
    (r'label="Yaroqlilik muddati"', r':label="t(\'erp.expirationDate\')"'),
    (r'label="Amallar"', r':label="t(\'common.action\')"'),
    (r'title="Nusxalash uchun bosing"', r':title="t(\'erp.clickToCopy\')"'),
]

def run():
    print("Enriching dictionary with all product and module translations...")
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

    # Update Vue files
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
