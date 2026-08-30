import os
import re
import json

NEW_KEYS = [
    # Adjustments
    ("newAdjustmentBtn", "Yangi korrektirovka (Bonus/Shtraf/Avans)", "New Adjustment (Bonus/Penalty/Advance)"),
    ("batchDelete", "Guruhli o'chirish", "Batch Delete"),
    ("workerCraftsman", "Xodim (Usta)", "Worker (Craftsman)"),
    ("adjustmentType", "Turi", "Type"),
    ("docTypeLabel", "Hujjat turi", "Document Type"),
    ("descriptionReason", "Tavsif (Sababi)", "Description (Reason)"),
    ("createdTime", "Kiritilgan vaqt", "Created Time"),
    ("bonusReward", "Bonus (Mukofot)", "Bonus (Reward)"),
    ("penaltyFine", "Jarima (Shtraf)", "Penalty (Fine)"),
    ("advancePayment", "Avans", "Advance"),
    ("bonusRewardOption", "Mukofot puli (Bonus)", "Bonus reward"),
    ("penaltyOption", "Jarima puli (Shtraf)", "Penalty fee"),
    ("advanceOption", "Oldindan to'lov (Avans)", "Advance payment"),
    ("adjustmentReasonPlaceholder", "Korrektirovka sababi yoki batafsil tavsifini yozing...", "Write adjustment reason or detailed description..."),

    # Timesheet
    ("newTimesheetBtn", "Yangi tabel yaratish", "Create New Timesheet"),
    ("timesheetDate", "Tabel sanasi", "Timesheet Date"),
    ("workerCount", "Xodimlar soni", "Worker Count"),
    ("timesheetStatus", "Tabel holati", "Timesheet Status"),
    ("personsSuffix", "nafar", "persons"),

    # Output (Vyrabotka)
    ("totalCompletedTasks", "Jami Bajarilgan Ishlar", "Total Completed Tasks"),
    ("totalCalculatedPayment", "Jami Hisoblangan To'lov", "Total Calculated Payment"),
    ("shortTermWorkers", "Qisqa Muddatli Ishchilar", "Short-term Workers"),
    ("avgTaskPrice", "O'rtacha Bitta Ish Narxi", "Average Task Price"),
    ("peopleSuffix", "kishi", "people"),
    ("startDate", "Boshlanish sanasi", "Start Date"),
    ("endDate", "Tugash sanasi", "End Date"),
    ("allWorkersFilter", "Barcha ishchilar", "All Workers"),
    ("searchTaskOrRemark", "Operatsiya yoki izoh qidirish...", "Search operation or remark..."),
    ("addNewWorkVolume", "Yangi Ish Hajmi Kiritish", "Add New Work Volume"),
    ("dateDayMonthYear", "Sana (Kun.Oy.Yil)", "Date (Day.Month.Year)"),
    ("workerCraftsmanName", "Ishchi / Usta Ismi", "Worker / Craftsman Name"),
    ("completedTaskOp", "Bajarilgan Ish / Operatsiya", "Completed Task / Operation"),
    ("tariffSalaryDollar", "Tarif / Ish Haqi ($)", "Tariff / Salary ($)"),
]

def run():
    print("Enriching StaffHR pages (Adjustment, Timesheet, Output)...")
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

    # 1. Update Adjustment.vue
    adj_p = '/home/xasanboy/ERP/Front/src/views/StaffHR/Adjustment.vue'
    with open(adj_p, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("Yangi korrektirovka (Bonus/Shtraf/Avans)", "{{ t('erp.newAdjustmentBtn') }}")
    content = content.replace("Guruhli o'chirish", "{{ t('erp.batchDelete') }}")
    content = content.replace('label="XODIM (USTA)"', ':label="t(\'erp.workerCraftsman\')"')
    content = content.replace('label="TURI"', ':label="t(\'erp.adjustmentType\')"')
    content = content.replace('label="MIQDORI ($)"', ':label="t(\'erp.miqdoriDollar\')"')
    content = content.replace('label="HISOBOT OYI"', ':label="t(\'erp.reportMonth\')"')
    content = content.replace('label="TAVSIF (SABABI)"', ':label="t(\'erp.descriptionReason\')"')
    content = content.replace('label="KIRITILGAN VAQT"', ':label="t(\'erp.createdTime\')"')
    content = content.replace('>Bonus (Mukofot)<', '>{{ t(\'erp.bonusReward\') }}<')
    content = content.replace('>Jarima (Shtraf)<', '>{{ t(\'erp.penaltyFine\') }}<')
    content = content.replace('>Avans<', '>{{ t(\'erp.advancePayment\') }}<')
    content = content.replace('label="Hujjat turi"', ':label="t(\'erp.docTypeLabel\')"')
    content = content.replace('label="Mukofot puli (Bonus)"', ':label="t(\'erp.bonusRewardOption\')"')
    content = content.replace('label="Jarima puli (Shtraf)"', ':label="t(\'erp.penaltyOption\')"')
    content = content.replace('label="Oldindan to\'lov (Avans)"', ':label="t(\'erp.advanceOption\')"')
    content = content.replace('label="Xodim"', ':label="t(\'erp.workerFullName\')"')
    content = content.replace('label="Miqdori ($)"', ':label="t(\'erp.miqdoriDollar\')"')
    content = content.replace('label="Hisobot oyi"', ':label="t(\'erp.reportMonth\')"')
    content = content.replace('label="Tavsif"', ':label="t(\'erp.tavsif\')"')
    content = content.replace('placeholder="Xodimni tanlang"', ':placeholder="t(\'erp.selectWorker\')"')
    content = content.replace('placeholder="Korrektirovka sababi yoki batafsil tavsifini yozing..."', ':placeholder="t(\'erp.adjustmentReasonPlaceholder\')"')
    content = content.replace('label="erp.worker"', ':label="t(\'erp.workerFullName\')"')

    with open(adj_p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Adjustment.vue!")

    # 2. Update Timesheet.vue
    ts_p = '/home/xasanboy/ERP/Front/src/views/StaffHR/Timesheet.vue'
    with open(ts_p, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("Yangi tabel yaratish", "{{ t('erp.newTimesheetBtn') }}")
    content = content.replace('label="Tabel sanasi"', ':label="t(\'erp.timesheetDate\')"')
    content = content.replace('label="Xodimlar soni"', ':label="t(\'erp.workerCount\')"')
    content = content.replace('label="Tabel holati"', ':label="t(\'erp.timesheetStatus\')"')
    content = content.replace('label="Kiritilgan vaqt"', ':label="t(\'erp.createdTime\')"')
    content = content.replace('{{ row.worker_count }} nafar', '{{ row.worker_count }} {{ t(\'erp.personsSuffix\') }}')
    content = content.replace('>Faol<', '>{{ t(\'erp.active\') }}<')

    with open(ts_p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Timesheet.vue!")

    # 3. Update Output.vue
    out_p = '/home/xasanboy/ERP/Front/src/views/StaffHR/Output.vue'
    with open(out_p, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace("JAMI BAJARILGAN ISHLAR", "{{ t('erp.totalCompletedTasks') }}")
    content = content.replace("JAMI HISOBLANGAN TO'LOV", "{{ t('erp.totalCalculatedPayment') }}")
    content = content.replace("QISQA MUDDATLI ISHCHILAR", "{{ t('erp.shortTermWorkers') }}")
    content = content.replace("O'RTACHA BITTA ISH NARXI", "{{ t('erp.avgTaskPrice') }}")
    content = content.replace("> ta<", "> {{ t('erp.unitsCount') }}<")
    content = content.replace("> kishi<", "> {{ t('erp.peopleSuffix') }}<")
    content = content.replace('start-placeholder="Boshlanish sanasi"', ':start-placeholder="t(\'erp.startDate\')"')
    content = content.replace('end-placeholder="Tugash sanasi"', ':end-placeholder="t(\'erp.endDate\')"')
    content = content.replace('placeholder="Barcha ishchilar"', ':placeholder="t(\'erp.allWorkersFilter\')"')
    content = content.replace('placeholder="Operatsiya yoki izoh qidirish..."', ':placeholder="t(\'erp.searchTaskOrRemark\')"')
    content = content.replace("Yangi Ish Hajmi Kiritish", "{{ t('erp.addNewWorkVolume') }}")
    content = content.replace('label="Sana (Kun.Oy.Yil)"', ':label="t(\'erp.dateDayMonthYear\')"')
    content = content.replace('label="Ishchi / Usta Ismi"', ':label="t(\'erp.workerCraftsmanName\')"')
    content = content.replace('label="Bajarilgan Ish / Operatsiya"', ':label="t(\'erp.completedTaskOp\')"')
    content = content.replace('label="Tarif / Ish Haqi ($)"', ':label="t(\'erp.tariffSalaryDollar\')"')
    content = content.replace('label="Kiritilgan Vaqti"', ':label="t(\'erp.createdTime\')"')

    with open(out_p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Output.vue!")

if __name__ == '__main__':
    run()
