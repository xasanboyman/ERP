import os
import re
import json

NEW_KEYS = [
    ("temporaryWorkers", "Vaqtinchalik / Yollanma Ishchilar", "Temporary / Hired Workers"),
    ("editWorkVolume", "Ish Hajmini Tahrirlash", "Edit Work Volume"),
    ("workDate", "Ish Sanasi (Kun / Oy / Yil)", "Work Date (Day / Month / Year)"),
    ("selectDate", "Sanani tanlang", "Select date"),
    ("workerNamePlaceholder", "Ismini yozing (masalan: Azizbek usta)", "Write name (e.g. Master Azizbek)"),
    ("operationNameLabel", "Bajarilgan Ish / Operatsiya Nomi", "Task / Operation Name"),
    ("operationNamePlaceholder", "Masalan: 150 dona burchak tikish, 400 ta qadoqlash...", "For example: Sewing 150 corners, packaging 400 units..."),
    ("completedQtyLabel", "Bajarilgan Miqdor", "Completed Quantity"),
    ("unitRateLabel", "Birlik Narxi ($)", "Unit Price ($)"),
    ("totalPaymentLabel", "Jami To'lov ($)", "Total Payment ($)"),
    ("additionalRemarkLabel", "Qo'shimcha Izoh", "Additional Remark"),
    ("additionalRemarkPlaceholder", "Vaqtinchalik ishchi yoki topshiriq haqida izoh...", "Remark about temporary worker or task..."),
]

def run():
    print("Fixing Output.vue and adding keys...")
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

    out_p = '/home/xasanboy/ERP/Front/src/views/StaffHR/Output.vue'
    with open(out_p, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("""        :title="
          dialogType === 'add'
            ? '{{ t('erp.addNewWorkVolume') }} (Vaqtinchalik / Yollanma Ishchilar)'
            : 'Ish Hajmini Tahrirlash'
        \"""", """:title="dialogType === 'add' ? `${t('erp.addNewWorkVolume')} (${t('erp.temporaryWorkers')})` : t('erp.editWorkVolume')\"""")

    content = content.replace('label="Ish Sanasi (Kun / Oy / Yil)"', ':label="t(\'erp.workDate\')"')
    content = content.replace('placeholder="Sanani tanlang"', ':placeholder="t(\'erp.selectDate\')"')
    content = content.replace('placeholder="Ismini yozing (masalan: Azizbek usta)"', ':placeholder="t(\'erp.workerNamePlaceholder\')"')
    content = content.replace('label="Bajarilgan Ish / Operatsiya Nomi"', ':label="t(\'erp.operationNameLabel\')"')
    content = content.replace('placeholder="Masalan: 150 dona burchak tikish, 400 ta qadoqlash..."', ':placeholder="t(\'erp.operationNamePlaceholder\')"')
    content = content.replace('label="Bajarilgan Miqdor"', ':label="t(\'erp.completedQtyLabel\')"')
    content = content.replace('label="Birlik Narxi ($)"', ':label="t(\'erp.unitRateLabel\')"')
    content = content.replace('label="Jami To\'lov ($)"', ':label="t(\'erp.totalPaymentLabel\')"')
    content = content.replace('label="Qo\'shimcha Izoh"', ':label="t(\'erp.additionalRemarkLabel\')"')
    content = content.replace('placeholder="Vaqtinchalik ishchi yoki topshiriq haqida izoh..."', ':placeholder="t(\'erp.additionalRemarkPlaceholder\')"')
    content = content.replace("O'chirish ({{ selectedIds.length }})", "{{ t('common.delete') }} ({{ selectedIds.length }})")
    content = content.replace("Yollanma / Vaqtinchalik", "{{ t('erp.temporaryWorkers') }}")
    content = content.replace(">Jami Bajarilgan Ishlar<", ">{{ t('erp.totalCompletedTasks') }}<")
    content = content.replace(">Jami Hisoblangan To'lov<", ">{{ t('erp.totalCalculatedPayment') }}<")
    content = content.replace(">Qisqa Muddatli Ishchilar<", ">{{ t('erp.shortTermWorkers') }}<")
    content = content.replace(">O'rtacha Bitta Ish Narxi<", ">{{ t('erp.avgTaskPrice') }}<")

    with open(out_p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed Output.vue successfully!")

if __name__ == '__main__':
    run()
