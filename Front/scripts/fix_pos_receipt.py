import os
import json

NEW_KEYS = [
    ("dateTimeColon", "Sana va Vaqt:", "Date and Time:"),
    ("cashierWorkerColon", "Kassir / Xodim:", "Cashier / Staff:"),
    ("paymentMethodColon", "To'lov Usuli:", "Payment Method:"),
    ("productNameUpper", "MAHSULOT NOMI", "PRODUCT NAME"),
    ("qtyTimesPriceUpper", "SONI × NARXI", "QTY × PRICE"),
    ("sumUpper", "SUMMA", "SUM"),
    ("totalSumUpper", "JAMI SUMMA:", "TOTAL AMOUNT:"),
    ("paidAmountColon", "To'langan Summa:", "Paid Amount:"),
    ("discountColon", "Chegirma:", "Discount:"),
    ("packageLabelColon", "Qadoq:", "Package:"),
]

def run():
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

    pos_p = '/home/xasanboy/ERP/Front/src/views/Sales/Pos.vue'
    with open(pos_p, 'r', encoding='utf-8') as f:
        c = f.read()

    c = c.replace('<span class="text-[var(--el-text-color-secondary)]">Sana va Vaqt:</span>', '<span class="text-[var(--el-text-color-secondary)]">{{ t(\'erp.dateTimeColon\') }}</span>')
    c = c.replace('<span class="text-[var(--el-text-color-secondary)]">Kassir / Xodim:</span>', '<span class="text-[var(--el-text-color-secondary)]">{{ t(\'erp.cashierWorkerColon\') }}</span>')
    c = c.replace('<span class="text-[var(--el-text-color-secondary)]">To\'lov Usuli:</span>', '<span class="text-[var(--el-text-color-secondary)]">{{ t(\'erp.paymentMethodColon\') }}</span>')
    c = c.replace('<span class="flex-1">MAHSULOT NOMI</span>', '<span class="flex-1">{{ t(\'erp.productNameUpper\') }}</span>')
    c = c.replace('<span class="w-220px text-right">SONI × NARXI</span>', '<span class="w-220px text-right">{{ t(\'erp.qtyTimesPriceUpper\') }}</span>')
    c = c.replace('<span class="w-150px text-right">SUMMA</span>', '<span class="w-150px text-right">{{ t(\'erp.sumUpper\') }}</span>')
    c = c.replace('<span>JAMI SUMMA:</span>', '<span>{{ t(\'erp.totalSumUpper\') }}</span>')
    c = c.replace('<span>To\'langan Summa:</span>', '<span>{{ t(\'erp.paidAmountColon\') }}</span>')
    c = c.replace('<span>Chegirma:</span>', '<span>{{ t(\'erp.discountColon\') }}</span>')
    c = c.replace('>Qadoq: ', '>{{ t(\'erp.packageLabelColon\') }} ')

    with open(pos_p, 'w', encoding='utf-8') as f:
        f.write(c)

    print("Updated POS receipt modal!")

if __name__ == '__main__':
    run()
