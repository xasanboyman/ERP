import os
import json
import re

NEW_KEYS = [
    ("nasiyaQarz", "Nasiya / Qarz", "Credit / Debt"),
    ("debtAmountColon", "Qarz:", "Debt:"),
    ("debtNasiyaColon", "Qarz / Nasiya:", "Debt / Credit:"),
    ("nasiyaSales", "Nasiya Xaridlari", "Credit Purchases"),
    ("debtHistory", "Qarzdorlik Tarixi", "Debt History"),
    ("repaymentHistory", "Qarz Qaytarganlik Tarixi", "Debt Repayment History"),
    ("noRepaymentsYet", "Hali qarz qaytarganlik yo'q", "No debt repayments yet"),
    ("debtPaymentReceipt", "OMBORXONA ERP — QARZ TO'LOV CHEKI", "WAREHOUSE ERP — DEBT PAYMENT RECEIPT"),
    ("repaidDebtAmount", "Qaytarilgan Qarz Summasi", "Repaid Debt Amount"),
    ("debtPaymentConfirmReceipt", "Qarz To'lovi — Tasdiqlash Cheki", "Debt Payment — Confirmation Receipt"),
    ("remainingTotalDebt", "Qolgan umumiy qarz:", "Remaining total debt:"),
    ("nasiyaDebt", "Nasiya Qarz", "Credit Debt"),
    ("debtDollar", "Qarz ($)", "Debt ($)"),
    ("oldDebtColon", "Eski qarz:", "Old debt:"),
    ("thankYouEnjoy", "Xaridingiz uchun rahmat! Salomat bo'ling!", "Thank you for your purchase! Stay healthy!"),
    ("printReceiptBtn", "Chop Etish (Print)", "Print Receipt"),
]

def run():
    print("Fixing NASIYA / QARZ across all files...")
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

    # 1. Pos.vue
    pos_p = '/home/xasanboy/ERP/Front/src/views/Sales/Pos.vue'
    with open(pos_p, 'r', encoding='utf-8') as f:
        pos_c = f.read()

    pos_c = pos_c.replace("""                <ElTag type="danger" effect="plain" class="font-bold uppercase rounded-pill mb-2px">
                  NASIYA / QARZ
                </ElTag>""", """                <ElTag type="danger" effect="plain" class="font-bold uppercase rounded-pill mb-2px">
                  {{ t('erp.debt').toUpperCase() }}
                </ElTag>""")

    pos_c = pos_c.replace("""                <div class="text-12px text-red-500 font-mono font-bold">
                  Qarz: ${{ formatMoney(scope.row.debt_amount) }}
                </div>""", """                <div class="text-12px text-red-500 font-mono font-bold">
                  {{ t('erp.debtAmountColon') }} ${{ formatMoney(scope.row.debt_amount) }}
                </div>""")

    pos_c = pos_c.replace('<span>QARZ / NASIYA:</span>', '<span>{{ t(\'erp.debtNasiyaColon\').toUpperCase() }}</span>')
    pos_c = pos_c.replace("Xaridingiz uchun rahmat! Salomat bo'ling!", "{{ t('erp.thankYouEnjoy') }}")
    pos_c = pos_c.replace("Chop Etish (Print)", "{{ t('erp.printReceiptBtn') }}")
    pos_c = pos_c.replace("Eski qarz:", "{{ t('erp.oldDebtColon') }}")

    with open(pos_p, 'w', encoding='utf-8') as f:
        f.write(pos_c)
    print("Updated Pos.vue!")

    # 2. Debtors.vue
    deb_p = '/home/xasanboy/ERP/Front/src/views/Sales/Debtors.vue'
    with open(deb_p, 'r', encoding='utf-8') as f:
        deb_c = f.read()

    deb_c = deb_c.replace('<span class="hds-label">Nasiya Xaridlar</span>', '<span class="hds-label">{{ t(\'erp.nasiyaSales\') }}</span>')
    deb_c = deb_c.replace('Nasiya Xaridlari', '{{ t(\'erp.nasiyaSales\') }}')
    deb_c = deb_c.replace('<div class="fin-label">Nasiya Qarz</div>', '<div class="fin-label">{{ t(\'erp.nasiyaDebt\') }}</div>')
    deb_c = deb_c.replace('title="Qarzdorlik Tarixi"', ':title="t(\'erp.debtHistory\')"')
    deb_c = deb_c.replace('label="Qarz ($)"', ':label="t(\'erp.debtDollar\')"')
    deb_c = deb_c.replace('Qarz Qaytarganlik Tarixi', '{{ t(\'erp.repaymentHistory\') }}')
    deb_c = deb_c.replace("Hali qarz qaytarganlik yo'q", '{{ t(\'erp.noRepaymentsYet\') }}')
    deb_c = deb_c.replace('OMBORXONA ERP — QARZ TO\'LOV CHEKI', '{{ t(\'erp.debtPaymentReceipt\') }}')
    deb_c = deb_c.replace('Qaytarilgan Qarz Summasi', '{{ t(\'erp.repaidDebtAmount\') }}')
    deb_c = deb_c.replace('title="Qarz To\'lovi — Tasdiqlash Cheki"', ':title="t(\'erp.debtPaymentConfirmReceipt\')"')
    deb_c = deb_c.replace('<span class="text-gray-400">Qolgan umumiy qarz:</span>', '<span class="text-gray-400">{{ t(\'erp.remainingTotalDebt\') }}</span>')

    with open(deb_p, 'w', encoding='utf-8') as f:
        f.write(deb_c)
    print("Updated Debtors.vue!")

    # 3. MobileScanner.vue
    mob_p = '/home/xasanboy/ERP/Front/src/views/Mobile/MobileScanner.vue'
    if os.path.exists(mob_p):
        with open(mob_p, 'r', encoding='utf-8') as f:
            mob_c = f.read()
        mob_c = mob_c.replace('📝 Nasiya / Qarz', '📝 {{ t(\'erp.debt\') }}')
        mob_c = mob_c.replace('📝 Nasiya', '📝 {{ t(\'erp.debt\') }}')
        with open(mob_p, 'w', encoding='utf-8') as f:
            f.write(mob_c)
        print("Updated MobileScanner.vue!")

    # 4. SalesHistory.vue
    sh_p = '/home/xasanboy/ERP/Front/src/views/Sales/SalesHistory.vue'
    if os.path.exists(sh_p):
        with open(sh_p, 'r', encoding='utf-8') as f:
            sh_c = f.read()
        sh_c = sh_c.replace('<ElOption label="Nasiya" value="nasiya" />', '<ElOption :label="t(\'erp.debt\')" value="nasiya" />')
        with open(sh_p, 'w', encoding='utf-8') as f:
            f.write(sh_c)
        print("Updated SalesHistory.vue!")

if __name__ == '__main__':
    run()
