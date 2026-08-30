import os
import re
import json

NEW_KEYS = [
    ("salaryPaymentHistory", "Oylik Maoshlar va To'lovlar Tarixi", "Salary and Payment History"),
    ("workerSalaryHistory", "Xodim Maosh Tarixi", "Worker Salary History"),
    ("totalPaid", "Jami to'langan", "Total Paid"),
    ("totalBonus", "Jami bonus", "Total Bonus"),
    ("totalDeductions", "Jami ushlanma", "Total Deductions"),
    ("allPaymentsHistory", "Barcha To'lovlar Tarixi", "All Payments History"),
    ("noPaymentsYet", "Ushbu xodimga hali to'lov amalga oshirilmagan", "No payments have been made to this worker yet"),
    ("transactionId", "Tranzaksiya ID", "Transaction ID"),
    ("paymentDate", "To'lov Sanasi", "Payment Date"),
    ("remarkInfo", "Izoh / Ma'lumot", "Remark / Info"),
    ("adjustmentsBonusPenalty", "Korrektirovkalar (Bonus & Jarima)", "Adjustments (Bonus & Penalty)"),
    ("noAdjustmentsYet", "Ushbu xodimga biriktirilgan bonus yoki jarimalar yo'q", "No bonus or penalties attached to this worker"),
    ("docType", "Hujjat Turi", "Document Type"),
    ("reasonRemark", "Sababi / Izoh", "Reason / Remark"),
]

def run():
    print("Enriching Salary details modal translations...")
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

    # Update Salary.vue
    s_path = '/home/xasanboy/ERP/Front/src/views/Salary/Salary.vue'
    with open(s_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("selectedWorker.name} — Oylik Maoshlar va To'lovlar Tarixi", "selectedWorker.name} — ${t('erp.salaryPaymentHistory')}")
    content = content.replace("'Xodim Maosh Tarixi'", "t('erp.workerSalaryHistory')")
    content = content.replace("Bo'lim: {{ selectedWorker.departmentName || '—' }}", "{{ t('erp.department') }}: {{ selectedWorker.departmentName || '—' }}")
    content = content.replace(">Asosiy oyligi:", ">{{ t('erp.baseSalaryLabel') }}:")
    content = content.replace(">Jami to'langan:", ">{{ t('erp.totalPaid') }}:")
    content = content.replace(">Jami bonus:", ">{{ t('erp.totalBonus') }}:")
    content = content.replace(">Jami ushlanma:", ">{{ t('erp.totalDeductions') }}:")
    content = content.replace("`Barcha To'lovlar Tarixi (${selectedWorkerSalaries.length} ta)`", "`${t('erp.allPaymentsHistory')} (${selectedWorkerSalaries.length} ta)`")
    content = content.replace("Ushbu xodimga hali to'lov amalga oshirilmagan", "{{ t('erp.noPaymentsYet') }}")
    content = content.replace('label="Tranzaksiya ID"', ':label="t(\'erp.transactionId\')"')
    content = content.replace('label="To\'lov Sanasi"', ':label="t(\'erp.paymentDate\')"')
    content = content.replace('label="Izoh / Ma\'lumot"', ':label="t(\'erp.remarkInfo\')"')
    content = content.replace('label="To\'langan Summa ($)"', ':label="t(\'erp.paidAmountDollar\')"')
    content = content.replace('label="O\'chirish"', ':label="t(\'common.delete\')"')
    content = content.replace("`Korrektirovkalar (Bonus & Jarima) (${selectedWorkerAdjustments.length} ta)`", "`${t('erp.adjustmentsBonusPenalty')} (${selectedWorkerAdjustments.length} ta)`")
    content = content.replace("Ushbu xodimga biriktirilgan bonus yoki jarimalar yo'q", "{{ t('erp.noAdjustmentsYet') }}")
    content = content.replace('label="Hujjat Turi"', ':label="t(\'erp.docType\')"')
    content = content.replace('label="Sababi / Izoh"', ':label="t(\'erp.reasonRemark\')"')

    with open(s_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Salary details modal in Salary.vue!")

if __name__ == '__main__':
    run()
