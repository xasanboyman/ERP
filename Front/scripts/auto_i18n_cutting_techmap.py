import os
import re
import json

NEW_KEYS = [
    ("techmapTitle", "Texnologik Xarita va Etaplar", "Techmap and Stages"),
    ("processStages", "Jarayon va Etaplar", "Processes and Stages"),
    ("processName", "Jarayon nomi", "Process Name"),
    ("stageName", "Etap nomi", "Stage Name"),
    ("cuttingTaskTitle", "Bichuv Topshiriqlari", "Cutting Tasks"),
    ("newCuttingTask", "Yangi Bichuv Topshirig'i", "New Cutting Task"),
    ("taskNumber", "Topshiriq №", "Task #"),
    ("cuttingQuantity", "Bichuv miqdori", "Cutting Quantity"),
]

def run():
    print("Enriching Cutting & Techmap views...")
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

    # Techmap.vue
    tm_p = '/home/xasanboy/ERP/Front/src/views/Techmap/Techmap.vue'
    with open(tm_p, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('label="Etap nomi"', ':label="t(\'erp.stageName\')"')
    content = content.replace('label="Jarayon nomi"', ':label="t(\'erp.processName\')"')
    with open(tm_p, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated Cutting & Techmap successfully!")

if __name__ == '__main__':
    run()
