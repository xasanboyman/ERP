import os
import re
from generate_cr_locale import convert_uz_to_cr, latin_to_cyrillic

def sync():
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()

    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    # Common vocabulary additions
    common_uz = """    actions: 'Amallar',
    status: 'Holati',
    category: 'Kategoriya',
    quantity: 'Miqdori',
    price: 'Narxi',
    total: 'Jami',
    date: 'Sana',
    name: 'Nomi',
    code: 'Kodi',
    phone: 'Telefon',
    address: 'Manzil',
    department: "Bo'lim",
    position: 'Lavozim',
    salary: 'Oylik maosh',
    worker: 'Xodim',
    save: 'Saqlash',
    close: 'Yopish',
    search: 'Qidirish',
    reset: 'Tozalash',
    add: "Qo'shish",
    edit: 'Tahrirlash',
    delete: "O'chirish",
    detail: 'Batafsil',
    export: 'Eksport',
    import: 'Import',
    print: 'Chop etish',
    confirm: 'Tasdiqlash',
    cancel: 'Bekor qilish',
    loading: 'Yuklanmoqda...',
    success: 'Muvaffaqiyatli',
    error: 'Xatolik',
    warning: 'Ogohlantirish',
    info: "Ma'lumot",
"""

    if 'actions:' not in uz_text:
        uz_text = uz_text.replace("common: {\n", "common: {\n" + common_uz)

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)

    # Re-generate cr.ts from complete uz.ts
    convert_uz_to_cr()
    print("Complete synchronization finished successfully!")

if __name__ == '__main__':
    sync()
