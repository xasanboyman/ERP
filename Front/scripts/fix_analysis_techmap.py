import json

NEW_KEYS = [
    ("selectAll", "Barchasini belgilash", "Select All"),
    ("sealMonthRecordHint", "Ushbu oydagi barcha savdo, xarajat va foyda ko'rsatkichlarini rasmiy arxivga muhrlab saqlash", "Archive and seal all sales, expenses, and profits for this month"),
    ("addNewStage", "Yangi etap qo'shish", "Add new stage"),
    ("editStage", "Etapni tahrirlash", "Edit stage"),
    ("addNewProcess", "Yangi jarayon yaratish", "Add new process"),
    ("editProcess", "Jarayonni tahrirlash", "Edit process"),
]

def run():
    print("Fixing Analysis.vue, Techmap.vue, and updating locales...")
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

    # 1. Analysis.vue
    an_p = '/home/xasanboy/ERP/Front/src/views/Dashboard/Analysis.vue'
    with open(an_p, 'r', encoding='utf-8') as f:
        an_t = f.read()
    an_t = an_t.replace(
        ": 'Ushbu oydagi barcha savdo, xarajat va foyda ko'rsatkichlarini rasmiy arxivga muhrlab saqlash'",
        ": t('erp.sealMonthRecordHint')"
    )
    with open(an_p, 'w', encoding='utf-8') as f:
        f.write(an_t)
    print("Fixed Analysis.vue")

    # 2. Techmap.vue
    tech_p = '/home/xasanboy/ERP/Front/src/views/Techmap/Techmap.vue'
    with open(tech_p, 'r', encoding='utf-8') as f:
        tech_t = f.read()
    tech_t = tech_t.replace(
        ":title=\"stageDialogType === 'add' ? 'Yangi etap qo'shish' : 'Etapni tahrirlash'\"",
        ":title=\"stageDialogType === 'add' ? t('erp.addNewStage') : t('erp.editStage')\""
    )
    tech_t = tech_t.replace(
        ":title=\"processDialogType === 'add' ? 'Yangi jarayon yaratish' : 'Jarayonni tahrirlash'\"",
        ":title=\"processDialogType === 'add' ? t('erp.addNewProcess') : t('erp.editProcess')\""
    )
    with open(tech_p, 'w', encoding='utf-8') as f:
        f.write(tech_t)
    print("Fixed Techmap.vue")

if __name__ == '__main__':
    run()
