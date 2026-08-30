import json
import re

EXTRA_KEYS = [
    ("hireNewWorker", "Yangi xodimni ishga olish", "Hire new worker"),
    ("editWorkerInfo", "Xodim ma'lumotlarini tahrirlash", "Edit worker information"),
    ("passwordOptionalDefault", "Parol kiriting (ixtiyoriy, sukut bo'yicha: 123456)", "Enter password (optional, default: 123456)"),
    ("editAdjustment", "Korrektirovkani tahrirlash", "Edit adjustment"),
    ("monthAlreadyClosedHint", "Ushbu oy allaqachon muhrlangan. Qayta hisoblash orqali arxivdagi ma'lumotlarni yangilash mumkin", "This month is already locked. Recalculating updates archived records"),
    ("monthOpenHint", "Oy ochiq", "Month is open"),
]

def run():
    print("Fixing broken single quotes and updating locales...")

    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    for k, uz_v, en_v in EXTRA_KEYS:
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

    # 1. Worker.vue
    worker_p = '/home/xasanboy/ERP/Front/src/views/Worker/Worker.vue'
    with open(worker_p, 'r', encoding='utf-8') as f:
        w_content = f.read()
    w_content = w_content.replace(
        "dialogType === 'add' ? 'Yangi xodimni ishga olish' : 'Xodim ma'lumotlarini tahrirlash'",
        "dialogType === 'add' ? t('erp.hireNewWorker') : t('erp.editWorkerInfo')"
    )
    w_content = w_content.replace(
        "? 'Parol kiriting (ixtiyoriy, sukut bo'yicha: 123456)'",
        "? t('erp.passwordOptionalDefault')"
    )
    with open(worker_p, 'w', encoding='utf-8') as f:
        f.write(w_content)
    print("Fixed Worker.vue")

    # 2. Adjustment.vue
    adj_p = '/home/xasanboy/ERP/Front/src/views/StaffHR/Adjustment.vue'
    with open(adj_p, 'r', encoding='utf-8') as f:
        adj_content = f.read()
    adj_content = adj_content.replace(
        ":title=\"dialogType === 'add' ? 'Korrektirovka qo'shish' : 'Korrektirovkani tahrirlash'\"",
        ":title=\"dialogType === 'add' ? t('erp.addAdjustment') : t('erp.editAdjustment')\""
    )
    with open(adj_p, 'w', encoding='utf-8') as f:
        f.write(adj_content)
    print("Fixed Adjustment.vue")

    # 3. Analysis.vue
    analysis_p = '/home/xasanboy/ERP/Front/src/views/Dashboard/Analysis.vue'
    with open(analysis_p, 'r', encoding='utf-8') as f:
        an_content = f.read()
    an_content = an_content.replace(
        "? 'Ushbu oy allaqachon muhrlangan. Qayta hisoblash orqali arxivdagi ma'lumotlarni yangilash mumkin'",
        "? t('erp.monthAlreadyClosedHint')"
    )
    with open(analysis_p, 'w', encoding='utf-8') as f:
        f.write(an_content)
    print("Fixed Analysis.vue")

if __name__ == '__main__':
    run()
