import os
import re
import json

NEW_KEYS = [
    ("workerIdSearch", "Ism/Xodim ID", "Name/Worker ID"),
    ("workerSearchPlaceholder", "Xodim ismi yoki login ID", "Worker name or login ID"),
    ("selectDepartment", "Bo'limni tanlang", "Select department"),
    ("newWorker", "Yangi xodim", "New Worker"),
    ("batchDismiss", "Guruhli bo'shatish", "Batch Dismiss"),
    ("workerId", "Xodim ID", "Worker ID"),
    ("name", "Ismi", "Name"),
    ("loginName", "Login nomi", "Login name"),
    ("role", "Roli", "Role"),
    ("regularWorker", "Oddiy xodim", "Regular worker"),
    ("departmentNameCol", "Bo'limi", "Department"),
    ("phoneNumber", "Telefon raqami", "Phone number"),
    ("baseSalaryDollar", "Asosiy maoshi ($)", "Base Salary ($)"),
    ("working", "Ishlamoqda", "Working"),
    ("dismissed", "Bo'shatilgan", "Dismissed"),
    ("dismiss", "Bo'shatish", "Dismiss"),
    ("enterWorkerName", "Iltimos, xodim ismini kiriting", "Please enter worker name"),
    ("loginPlaceholder", "Tizimga kirish nomi, masalan: anvars", "Login name, e.g.: anvars"),
    ("selectRole", "Rolni tanlang", "Select role"),
    ("baseSalaryLabel", "Asosiy maoshi", "Base salary"),
    ("selectDatePlaceholder", "Sana tanlang", "Select date"),
    ("systemPassword", "Tizim paroli", "System password"),
    ("adminPassword", "Admin paroli", "Admin password"),
]

REPLACEMENTS = [
    (r'label="Ism/Xodim ID"', r':label="t(\'erp.workerIdSearch\')"'),
    (r'placeholder="Xodim ismi yoki login ID"', r':placeholder="t(\'erp.workerSearchPlaceholder\')"'),
    (r'placeholder="Bo\'limni tanlang"', r':placeholder="t(\'erp.selectDepartment\')"'),
    (r'>\s*Yangi xodim\s*<', r'>{{ t("erp.newWorker") }}<'),
    (r'>\s*Guruhli bo\'shatish\s*<', r'>{{ t("erp.batchDismiss") }}<'),
    (r'label="Xodim ID"', r':label="t(\'erp.workerId\')"'),
    (r'label="Ismi"', r':label="t(\'erp.name\')"'),
    (r'label="Login nomi"', r':label="t(\'erp.loginName\')"'),
    (r'label="Roli"', r':label="t(\'erp.role\')"'),
    (r'label="Bo\'limi"', r':label="t(\'erp.departmentNameCol\')"'),
    (r'label="Telefon raqami"', r':label="t(\'erp.phoneNumber\')"'),
    (r'label="Asosiy maoshi \(\$\)"', r':label="t(\'erp.baseSalaryDollar\')"'),
    (r'label="Asosiy maoshi"', r':label="t(\'erp.baseSalaryLabel\')"'),
    (r'>\s*Oddiy xodim\s*<', r'>{{ t("erp.regularWorker") }}<'),
    (r'scope\.row\.role \|\| \'Oddiy xodim\'', r'scope.row.role || t(\'erp.regularWorker\')'),
    (r'>\s*Ishlamoqda\s*<', r'>{{ t("erp.working") }}<'),
    (r'scope\.row\.status === 1 \? \'Ishlamoqda\' : "Bo\'shatilgan"', r'scope.row.status === 1 ? t(\'erp.working\') : t(\'erp.dismissed\')'),
    (r'>\s*Bo\'shatish\s*<', r'>{{ t("erp.dismiss") }}<'),
    (r'placeholder="Iltimos, xodim ismini kiriting"', r':placeholder="t(\'erp.enterWorkerName\')"'),
    (r'placeholder="Tizimga kirish nomi, masalan: anvars"', r':placeholder="t(\'erp.loginPlaceholder\')"'),
    (r'placeholder="Rolni tanlang"', r':placeholder="t(\'erp.selectRole\')"'),
    (r'placeholder="Sana tanlang"', r':placeholder="t(\'erp.selectDatePlaceholder\')"'),
    (r'label="Tizim paroli"', r':label="t(\'erp.systemPassword\')"'),
    (r'label="Admin paroli"', r':label="t(\'erp.adminPassword\')"'),
]

def run():
    print("Enriching Worker and module translations...")
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

    # Update Worker.vue
    w_path = '/home/xasanboy/ERP/Front/src/views/Worker/Worker.vue'
    with open(w_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for pat, rep in REPLACEMENTS:
        content = re.sub(pat, rep, content)

    with open(w_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Worker.vue!")

if __name__ == '__main__':
    run()
