import os
import re
import json

VIEWS_DIR = '/home/xasanboy/ERP/Front/src/views'

NEW_ERP_KEYS = [
    ("todaySales", "Bugungi Sotuvlar", "Today's Sales"),
    ("soldProducts", "Sotilgan Mahsulotlar", "Sold Products"),
    ("todayGrossRevenue", "Bugungi Jami Tushum", "Today's Gross Revenue"),
    ("currentCashier", "Joriy Kassir / Xodim", "Current Cashier / Worker"),
    ("newPosSale", "Yangi Sotuv (POS Kassa)", "New POS Sale"),
    ("receiptNumber", "Chek Raqami", "Receipt #"),
    ("dateTime", "Sana va Vaqt", "Date and Time"),
    ("cashier", "Kassir", "Cashier"),
    ("paymentStatus", "To'lov Holati", "Payment Status"),
    ("productQuantity", "Mahsulotlar Soni", "Products Count"),
    ("totalAmountDollar", "Jami Summa ($)", "Total Amount ($)"),
    ("receipt", "Chek", "Receipt"),
    ("cash", "Naqd", "Cash"),
    ("card", "Karta", "Card"),
    ("debt", "Nasiya / Qarz", "Credit / Debt"),
    ("bankTransfer", "Bank o'tkazmasi", "Bank Transfer"),
    ("allPaymentMethods", "Barcha to'lov usullari", "All payment methods"),
    ("searchReceiptPlaceholder", "Chek #, Kassir yoki Mahsulot izlash...", "Search receipt #, cashier or product..."),
    ("totalDebts", "Jami Nasiya Qarzlar", "Total Debts"),
    ("debtorsCount", "Qarzdorlar Soni", "Debtors Count"),
    ("totalRepaid", "Jami Qaytarilgan", "Total Repaid"),
    ("customerDebtor", "Mijoz / Qarzdor", "Customer / Debtor"),
    ("totalDebt", "Umumiy Qarz", "Total Debt"),
    ("remainingDebt", "Qolgan Qarz", "Remaining Debt"),
    ("repaid", "Qaytarilgan", "Repaid"),
    ("lastTransaction", "Oxirgi bitim", "Last Transaction"),
    ("worker", "Xodim", "Worker"),
    ("baseSalary", "Asosiy oylik", "Base Salary"),
    ("dailyRate", "Kunlik stavka", "Daily Rate"),
    ("workedDays", "Ishlagan kunlari", "Worked Days"),
    ("workedHours", "Ishlagan soatlari", "Worked Hours"),
    ("bonusPlus", "Bonus (+)", "Bonus (+)"),
    ("deductionMinus", "Ushlanma (-)", "Deduction (-)"),
    ("calculatedSalary", "Hisoblangan oylik", "Calculated Salary"),
    ("paidSalary", "To'langan oylik", "Paid Salary"),
    ("balanceDebt", "Qoldiq (Qarz)", "Balance (Debt)"),
    ("productName", "Mahsulot Nomi", "Product Name"),
    ("barcode", "Shtrix Kodi", "Barcode"),
    ("costPrice", "Tannarxi", "Cost Price"),
    ("sellingPrice", "Sotuv Narxi", "Selling Price"),
    ("availableQuantity", "Mavjud Miqdor", "Available Quantity"),
    ("unit", "O'lchov birligi", "Unit of Measure"),
    ("minQuantity", "Min Miqdor", "Min Quantity"),
    ("barcodeOrBrand", "Shtrix-kod / Brend", "Barcode / Brand"),
    ("availableStock", "Mavjud Ombor", "Available Stock"),
    ("sellingPriceDollar", "Sotish Narxi ($)", "Selling Price ($)"),
    ("cartPosKassa", "Savat / POS Kassa", "Cart / POS Checkout"),
    ("cartEmpty", "Savat bo'sh", "Cart is empty"),
    ("pickProductHint", "Chap tarafdan mahsulot tanlang yoki shtrix-kod skanerlang", "Select a product from the left or scan a barcode"),
    ("selectPaymentMethod", "To'lov Usulini Tanlang:", "Select Payment Method:"),
    ("paidAmountDollar", "To'langan Summa ($):", "Paid Amount ($):"),
    ("fullPaid", "Toliq", "Full"),
    ("debtorCustomerName", "Qarzdor / Mijoz Ismi:", "Debtor / Customer Name:"),
    ("oldDebt", "Eski qarz:", "Old debt:"),
    ("searchCustomerPlaceholder", "Mijoz ismini kiriting yoki tanlang...", "Enter or select customer name..."),
    ("newDebtAmount", "Yangi Qarz / Nasiya Summasi:", "New Debt Amount:"),
    ("totalProducts", "Mahsulotlar jami:", "Total Products:"),
    ("discountDollar", "Chegirma ($):", "Discount ($):"),
    ("totalPayment", "Jami To'lov:", "Total Payment:"),
    ("completeSale", "SOTISHNI YAKUNLASH", "COMPLETE SALE"),
    ("salesReceipt", "Sotuv Cheki", "Sales Receipt"),
    ("printReceipt", "Chekni Chop Etish", "Print Receipt"),
    ("scanOrSearchPlaceholder", "Shtrix-kod skanerlang yoki izlang (masalan: 100*47800...)...", "Scan barcode or search (e.g. 100*47800...)..."),
    ("allCategories", "Barchasi", "All"),
    ("newSaleRegister", "Yangi Sotuv Rasmiylashtirish (POS Kassa)", "Register New Sale (POS)"),
    ("quantity", "Soni:", "Qty:"),
    ("phone", "Telefon", "Phone"),
    ("category", "Kategoriya", "Category")
]

REPLACEMENTS = [
    # POS Modal specific
    (r'title="Yangi Sotuv Rasmiylashtirish \(POS Kassa\)"', r':title="t(\'erp.newSaleRegister\')"'),
    (r'label="Shtrix-kod / Brend"', r':label="t(\'erp.barcodeOrBrand\')"'),
    (r'label="Mavjud Ombor"', r':label="t(\'erp.availableStock\')"'),
    (r'label="Sotish Narxi \(\$\)"', r':label="t(\'erp.sellingPriceDollar\')"'),
    (r'>\s*Savat / POS Kassa\s*<', r'>{{ t("erp.cartPosKassa") }}<'),
    (r'>\s*Savat bo\'sh\s*<', r'>{{ t("erp.cartEmpty") }}<'),
    (r'>\s*Chap tarafdan mahsulot tanlang yoki shtrix-kod skanerlang\s*<', r'>{{ t("erp.pickProductHint") }}<'),
    (r'>\s*To\'lov Usulini Tanlang:\s*<', r'>{{ t("erp.selectPaymentMethod") }}<'),
    (r'>\s*To\'langan Summa \(\$\):\s*<', r'>{{ t("erp.paidAmountDollar") }}<'),
    (r'>\s*Toliq\s*<', r'>{{ t("erp.fullPaid") }}<'),
    (r'>\s*Qarzdor / Mijoz Ismi:\s*<', r'>{{ t("erp.debtorCustomerName") }}<'),
    (r'>\s*Eski qarz:\s*<', r'>{{ t("erp.oldDebt") }}<'),
    (r'placeholder="Mijoz ismini kiriting yoki tanlang\.\.\."', r':placeholder="t(\'erp.searchCustomerPlaceholder\')"'),
    (r'>\s*Yangi Qarz / Nasiya Summasi:\s*<', r'>{{ t("erp.newDebtAmount") }}<'),
    (r'>\s*Mahsulotlar jami:\s*<', r'>{{ t("erp.totalProducts") }}<'),
    (r'>\s*Chegirma \(\$\):\s*<', r'>{{ t("erp.discountDollar") }}<'),
    (r'>\s*Jami To\'lov:\s*<', r'>{{ t("erp.totalPayment") }}<'),
    (r'SOTISHNI YAKUNLASH \(\$\{\{\s*formatMoney\(grandTotal\)\s*\}\}\)', r'{{ t("erp.completeSale") }} (${{ formatMoney(grandTotal) }})'),
    (r'title="Sotuv Cheki"', r':title="t(\'erp.salesReceipt\')"'),
    (r'>\s*Chekni Chop Etish\s*<', r'>{{ t("erp.printReceipt") }}<'),
    (r'placeholder="Shtrix-kod skanerlang yoki izlang \(masalan: 100\*47800\.\.\.\)\.\.\."', r':placeholder="t(\'erp.scanOrSearchPlaceholder\')"'),
    (r'>\s*Barchasi\s*<', r'>{{ t("erp.allCategories") }}<'),
    (r'>\s*Soni:\s*<', r'>{{ t("erp.quantity") }}<'),

    # General Buttons
    (r'>\s*Qidirish\s*<', r'>{{ t("common.search") }}<'),
    (r'>\s*Tozalash\s*<', r'>{{ t("common.reset") }}<'),
    (r'>\s*Saqlash\s*<', r'>{{ t("common.save") }}<'),
    (r'>\s*Yopish\s*<', r'>{{ t("common.close") }}<'),
    (r'>\s*Tahrirlash\s*<', r'>{{ t("common.edit") }}<'),
    (r'>\s*O\'chirish\s*<', r'>{{ t("common.delete") }}<'),
    (r'>\s*Batafsil\s*<', r'>{{ t("common.detail") }}<'),
    (r'>\s*Tasdiqlash\s*<', r'>{{ t("common.confirm") }}<'),
    (r'>\s*Bekor qilish\s*<', r'>{{ t("common.cancel") }}<'),
    (r'>\s*Yangi qo\'shish\s*<', r'>{{ t("exampleDemo.add") }}<'),

    # POS & Sales
    (r'>\s*Bugungi Sotuvlar\s*<', r'>{{ t("erp.todaySales") }}<'),
    (r'>\s*Sotilgan Mahsulotlar\s*<', r'>{{ t("erp.soldProducts") }}<'),
    (r'>\s*Bugungi Jami Tushum\s*<', r'>{{ t("erp.todayGrossRevenue") }}<'),
    (r'>\s*Joriy Kassir / Xodim\s*<', r'>{{ t("erp.currentCashier") }}<'),
    (r'>\s*\+\s*Yangi Sotuv \(POS Kassa\)\s*<', r'>+ {{ t("erp.newPosSale") }}<'),
    (r'label="Chek Raqami"', r':label="t(\'erp.receiptNumber\')"'),
    (r'label="Sana va Vaqt"', r':label="t(\'erp.dateTime\')"'),
    (r'label="Kassir"', r':label="t(\'erp.cashier\')"'),
    (r'label="To\'lov Holati"', r':label="t(\'erp.paymentStatus\')"'),
    (r'label="Mahsulotlar Soni"', r':label="t(\'erp.productQuantity\')"'),
    (r'label="Jami Summa \(\$\)"', r':label="t(\'erp.totalAmountDollar\')"'),
    (r'label="Chek"', r':label="t(\'erp.receipt\')"'),
    (r'label="Naqd"', r':label="t(\'erp.cash\')"'),
    (r'label="Karta"', r':label="t(\'erp.card\')"'),
    (r'label="Nasiya / Qarz"', r':label="t(\'erp.debt\')"'),
    (r'label="Bank o\'tkazmasi"', r':label="t(\'erp.bankTransfer\')"'),
    (r'placeholder="Barcha to\'lov usullari"', r':placeholder="t(\'erp.allPaymentMethods\')"'),
    (r'placeholder="Chek #, Kassir yoki Mahsulot izlash\.\.\."', r':placeholder="t(\'erp.searchReceiptPlaceholder\')"'),

    # Debtors
    (r'>\s*Jami Nasiya Qarzlar\s*<', r'>{{ t("erp.totalDebts") }}<'),
    (r'>\s*Qarzdorlar Soni\s*<', r'>{{ t("erp.debtorsCount") }}<'),
    (r'>\s*Jami Qaytarilgan\s*<', r'>{{ t("erp.totalRepaid") }}<'),
    (r'>\s*Mijoz / Qarzdor\s*<', r'>{{ t("erp.customerDebtor") }}<'),
    (r'label="Mijoz / Qarzdor"', r':label="t(\'erp.customerDebtor\')"'),
    (r'label="Telefon"', r':label="t(\'erp.phone\')"'),
    (r'label="Umumiy Qarz"', r':label="t(\'erp.totalDebt\')"'),
    (r'label="Qolgan Qarz"', r':label="t(\'erp.remainingDebt\')"'),
    (r'label="Qaytarilgan"', r':label="t(\'erp.repaid\')"'),
    (r'label="Oxirgi bitim"', r':label="t(\'erp.lastTransaction\')"'),

    # Salary & HR
    (r'label="Xodim"', r':label="t(\'erp.worker\')"'),
    (r'label="Lavozim"', r':label="t(\'erp.position\')"'),
    (r'label="Bo\'lim"', r':label="t(\'erp.department\')"'),
    (r'label="Asosiy oylik"', r':label="t(\'erp.baseSalary\')"'),
    (r'label="Kunlik stavka"', r':label="t(\'erp.dailyRate\')"'),
    (r'label="Ishlagan kunlari"', r':label="t(\'erp.workedDays\')"'),
    (r'label="Ishlagan soatlari"', r':label="t(\'erp.workedHours\')"'),
    (r'label="Bonus \(\+\)"', r':label="t(\'erp.bonusPlus\')"'),
    (r'label="Ushlanma \(-\)"', r':label="t(\'erp.deductionMinus\')"'),
    (r'label="Hisoblangan oylik"', r':label="t(\'erp.calculatedSalary\')"'),
    (r'label="To\'langan oylik"', r':label="t(\'erp.paidSalary\')"'),
    (r'label="Qoldiq \(Qarz\)"', r':label="t(\'erp.balanceDebt\')"'),
    (r'label="To\'lov holati"', r':label="t(\'erp.paymentStatus\')"'),

    # Products
    (r'label="Mahsulot Nomi"', r':label="t(\'erp.productName\')"'),
    (r'label="Shtrix Kodi"', r':label="t(\'erp.barcode\')"'),
    (r'label="Kategoriya"', r':label="t(\'erp.category\')"'),
    (r'label="Tannarxi"', r':label="t(\'erp.costPrice\')"'),
    (r'label="Sotuv Narxi"', r':label="t(\'erp.sellingPrice\')"'),
    (r'label="Mavjud Miqdor"', r':label="t(\'erp.availableQuantity\')"'),
    (r'label="O\'lchov birligi"', r':label="t(\'erp.unit\')"'),
    (r'label="Min Miqdor"', r':label="t(\'erp.minQuantity\')"'),
]

def run():
    print("Converting views and adding full erp keys...")
    
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'
    
    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    for k, uz_v, en_v in NEW_ERP_KEYS:
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

    vue_files = []
    for root, dirs, files in os.walk(VIEWS_DIR):
        for file in files:
            if file.endswith('.vue'):
                vue_files.append(os.path.join(root, file))

    updated_count = 0
    for vf in vue_files:
        with open(vf, 'r', encoding='utf-8') as f:
            content = f.read()

        orig = content
        for pattern, repl in REPLACEMENTS:
            content = re.sub(pattern, repl, content)

        if content != orig:
            if "useI18n" not in content:
                content = re.sub(r'(<script[^>]*>)', r"\1\nimport { useI18n } from '@/hooks/web/useI18n'\nconst { t } = useI18n()", content, count=1)
            elif "const { t } = useI18n()" not in content and "const { t," not in content:
                content = re.sub(r'(<script[^>]*>)', r"\1\nconst { t } = useI18n()", content, count=1)

            with open(vf, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_count += 1
            print(f"Updated: {os.path.basename(vf)}")

    print(f"Total updated vue views: {updated_count}")

if __name__ == '__main__':
    run()
