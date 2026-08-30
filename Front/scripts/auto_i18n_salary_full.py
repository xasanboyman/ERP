import os
import re
import json

NEW_KEYS = [
    ("reportMonth", "Hisobot Oyi", "Report Month"),
    ("workerNameSearch", "Xodim ismi...", "Worker name..."),
    ("selectStatus", "Holatni tanlang", "Select status"),
    ("paid", "To'langan", "Paid"),
    ("pending", "Kutilmoqda", "Pending"),
    ("distributePayroll", "Maoshlarni tarqatish (Payroll)", "Distribute Payroll"),
    ("baseDollar", "Asosiy ($)", "Base ($)"),
    ("prevMonth", "O'tgan", "Previous"),
    ("selectedMonth", "Tanlangan", "Selected"),
    ("bonusDollar", "Bonus ($)", "Bonus ($)"),
    ("penaltyDollar", "Ushlanma ($)", "Deduction ($)"),
    ("netSalaryDollar", "Sof maosh ($)", "Net Salary ($)"),
    ("nextMonth", "Keyingi", "Next"),
]

def run():
    print("Enriching Salary page translations...")
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

    content = re.sub(r'label="Hisobot Oyi"', r':label="t(\'erp.reportMonth\')"', content)
    content = re.sub(r':label="t\(\'erp\.worker\'\)"', r':label="t(\'erp.workerFullName\')"', content)
    content = re.sub(r'placeholder="Xodim ismi\.\.\."', r':placeholder="t(\'erp.workerNameSearch\')"', content)
    content = re.sub(r'placeholder="Holatni tanlang"', r':placeholder="t(\'erp.selectStatus\')"', content)
    content = re.sub(r'label="✓ To\'langan"', r':label="\'✓ \' + t(\'erp.paid\')"', content)
    content = re.sub(r'label="⏳ Kutilmoqda"', r':label="\'⏳ \' + t(\'erp.pending\')"', content)
    content = re.sub(r'>\s*Maoshlarni tarqatish \(Payroll\)\s*<', r'>{{ t("erp.distributePayroll") }}<', content)
    content = re.sub(r'label="Asosiy \(\$\)"', r':label="t(\'erp.baseDollar\')"', content)
    content = re.sub(r':label="`O\'tgan \(\$\{prevMonthStr\}\)`"', r':label="`${t(\'erp.prevMonth\')} (${prevMonthStr})`"', content)
    content = re.sub(r':label="`Tanlangan \(\$\{selectedMonthStr\}\)`"', r':label="`${t(\'erp.selectedMonth\')} (${selectedMonthStr})`"', content)
    content = re.sub(r'label="Bonus \(\$\)"', r':label="t(\'erp.bonusDollar\')"', content)
    content = re.sub(r'label="Ushlanma \(\$\)"', r':label="t(\'erp.penaltyDollar\')"', content)
    content = re.sub(r'label="Sof maosh \(\$\)"', r':label="t(\'erp.netSalaryDollar\')"', content)
    content = re.sub(r'scope\.row\.isSelectedMonthPaid \? "To\'langan" : \'Kutilmoqda\'', r'scope.row.isSelectedMonthPaid ? t(\'erp.paid\') : t(\'erp.pending\')', content)
    content = re.sub(r':label="`Keyingi \(\$\{nextMonthStr\}\)`"', r':label="`${t(\'erp.nextMonth\')} (${nextMonthStr})`"', content)
    content = re.sub(r'label="Amallar"', r':label="t(\'common.action\')"', content)
    content = re.sub(r'>\s*✓ To\'langan\s*<', r'>✓ {{ t("erp.paid") }}<', content)

    with open(s_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Salary.vue!")

if __name__ == '__main__':
    run()
