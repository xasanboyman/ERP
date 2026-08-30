import os
import re
import json

VIEWS_DIR = '/home/xasanboy/ERP/Front/src/views'

# Additional phrases to map
PHRASE_MAP = [
    # Debtors Modal
    ("Amallar", "Amallar", "Actions"),
    ("Izoh", "Izoh", "Remark"),
    ("To'liq", "To'liq", "Full"),
    ("Ismi yoki tanlang...", "Ismi yoki tanlang...", "Name or select..."),
    ("Qarzdorlik tarixini ko'rish uchun bosing", "Qarzdorlik tarixini ko'rish uchun bosing", "Click to view debt history"),

    # Worker & HR
    ("Barcha bo'limlar", "Barcha bo'limlar", "All departments"),
    ("Barcha lavozimlar", "Barcha lavozimlar", "All positions"),
    ("Xodim ismi yoki telefon...", "Xodim ismi yoki telefon...", "Worker name or phone..."),
    ("F.I.Sh.", "F.I.Sh.", "Full Name"),
    ("Ish turi", "Ish turi", "Job type"),
    ("Stavka", "Stavka", "Rate"),
    ("Maosh", "Maosh", "Salary"),
    ("Oylik", "Oylik", "Monthly"),
    ("Kunlik", "Kunlik", "Daily"),
    ("Dona-bay", "Dona-bay", "Piece-rate"),
    ("Ishga kirgan sana", "Ishga kirgan sana", "Hire date"),
    ("Holati", "Holati", "Status"),
    ("Faol", "Faol", "Active"),
    ("Nofaol", "Nofaol", "Inactive"),

    # Salary
    ("Oyliklar jadvali", "Oyliklar jadvali", "Payroll sheet"),
    ("Hisoblash", "Hisoblash", "Calculate"),
    ("To'lov qilish", "To'lov qilish", "Make Payment"),
    ("Oyni tanlang", "Oyni tanlang", "Select month"),
    ("Hisoblangan", "Hisoblangan", "Calculated"),
    ("To'langan", "To'langan", "Paid"),
    ("Qoldiq", "Qoldiq", "Balance"),
    ("To'lov", "To'lov", "Payment"),
    ("To'landi", "To'landi", "Paid"),
    ("Kutilmoqda", "Kutilmoqda", "Pending"),

    # Product
    ("Mahsulot qidirish...", "Mahsulot qidirish...", "Search product..."),
    ("Kategoriyani tanlang", "Kategoriyani tanlang", "Select category"),
    ("Yangi Mahsulot Qo'shish", "Yangi Mahsulot Qo'shish", "Add New Product"),
    ("Rasmi", "Rasmi", "Image"),
    ("Miqdori", "Miqdori", "Quantity"),
    ("Birligi", "Birligi", "Unit"),
    ("Tannarx", "Tannarx", "Cost price"),
    ("Sotuv narx", "Sotuv narx", "Selling price"),
    ("Ombor", "Ombor", "Warehouse"),

    # Common
    ("Yuklanmoqda...", "Yuklanmoqda...", "Loading..."),
    ("Ma'lumot topilmadi", "Ma'lumot topilmadi", "No data found"),
    ("Tasdiqlaysizmi?", "Tasdiqlaysizmi?", "Are you sure?"),
    ("Muvaffaqiyatli saqlandi", "Muvaffaqiyatli saqlandi", "Saved successfully"),
    ("Muvaffaqiyatli o'chirildi", "Muvaffaqiyatli o'chirildi", "Deleted successfully"),
]

def to_camel(s):
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
    words = s.split()
    if not words:
        return 'key'
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])

def run():
    print("Scanning and translating all remaining UI phrases...")
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    replacements = []

    for phrase, uz_val, en_val in PHRASE_MAP:
        key = to_camel(phrase)
        uz_entry = f"    {key}: {json.dumps(uz_val, ensure_ascii=False)},"
        en_entry = f"    {key}: {json.dumps(en_val, ensure_ascii=False)},"
        if f"{key}:" not in uz_text:
            uz_text = uz_text.replace("erp: {", "erp: {\n" + uz_entry)
        if f"{key}:" not in en_text:
            en_text = en_text.replace("erp: {", "erp: {\n" + en_entry)

        # Regex for tag content
        replacements.append((re.compile(r'>\s*' + re.escape(phrase) + r'\s*<'), f'>{{{{ t("erp.{key}") }}}}<'))
        # Regex for attributes
        replacements.append((re.compile(r'label="' + re.escape(phrase) + r'"'), f':label="t(\'erp.{key}\')"'))
        replacements.append((re.compile(r'placeholder="' + re.escape(phrase) + r'"'), f':placeholder="t(\'erp.{key}\')"'))
        replacements.append((re.compile(r'title="' + re.escape(phrase) + r'"'), f':title="t(\'erp.{key}\')"'))

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_text)

    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()

    # Update all Vue files
    for root, dirs, files in os.walk(VIEWS_DIR):
        for file in files:
            if file.endswith('.vue'):
                p = os.path.join(root, file)
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()

                orig = content
                for pat, rep in replacements:
                    content = pat.sub(rep, content)

                if content != orig:
                    if "useI18n" not in content:
                        content = re.sub(r'(<script[^>]*>)', r"\1\nimport { useI18n } from '@/hooks/web/useI18n'\nconst { t } = useI18n()", content, count=1)
                    elif "const { t } = useI18n()" not in content and "const { t," not in content:
                        content = re.sub(r'(<script[^>]*>)', r"\1\nconst { t } = useI18n()", content, count=1)

                    with open(p, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated: {file}")

if __name__ == '__main__':
    run()
