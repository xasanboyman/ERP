import os
import json

def run():
    uz_p = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_p = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_p, 'r', encoding='utf-8') as f:
        uz_t = f.read()
    with open(en_p, 'r', encoding='utf-8') as f:
        en_t = f.read()

    if 'shortTermWorkers:' not in uz_t.split('erp: {')[1].split('}')[0]:
        uz_t = uz_t.replace("erp: {", "erp: {\n    shortTermWorkers: 'Qisqa Muddatli Ishchilar',")
    if 'shortTermWorkers:' not in en_t.split('erp: {')[1].split('}')[0]:
        en_t = en_t.replace("erp: {", "erp: {\n    shortTermWorkers: 'Short-term Workers',")

    with open(uz_p, 'w', encoding='utf-8') as f:
        f.write(uz_t)
    with open(en_p, 'w', encoding='utf-8') as f:
        f.write(en_t)

    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()

    out_p = '/home/xasanboy/ERP/Front/src/views/StaffHR/Output.vue'
    with open(out_p, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('<span class="stat-unit">ta</span>', '<span class="stat-unit">{{ t(\'erp.unitsCount\') }}</span>')
    content = content.replace('<span class="stat-unit">kishi</span>', '<span class="stat-unit">{{ t(\'erp.peopleSuffix\') }}</span>')

    with open(out_p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed Output.vue units!")

if __name__ == '__main__':
    run()
