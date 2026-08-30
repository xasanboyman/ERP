import os
import re
import json

def slugify(text: str) -> str:
    clean = re.sub(r'[\(\)\$\%\,\.\:\;\!\?\/\\\'\`\‘\ʻ\’\"\-\_]+', ' ', text).strip()
    words = clean.split()
    if not words:
        return "text"
    words = [w for w in words if w]
    res = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    if res[0].isdigit():
        res = 't_' + res
    return res[:35]

def latin_to_cyrillic(text: str) -> str:
    if not text or not isinstance(text, str):
        return text

    pairs = [
        ("Sh", "Ш"), ("SH", "Ш"), ("Ch", "Ч"), ("CH", "Ч"),
        ("Yo", "Ё"), ("YO", "Ё"), ("Yu", "Ю"), ("YU", "Ю"),
        ("Ya", "Я"), ("YA", "Я"), ("Ye", "Е"), ("YE", "Е"),
        ("O'", "Ў"), ("O`", "Ў"), ("O‘", "Ў"), ("Oʻ", "Ў"), ("O’", "Ў"),
        ("G'", "Ғ"), ("G`", "Ғ"), ("G‘", "Ғ"), ("Gʻ", "Ғ"), ("G’", "Ғ"),

        ("sh", "ш"), ("ch", "ч"), ("yo", "ё"), ("yu", "ю"),
        ("ya", "я"), ("ye", "е"),
        ("o'", "ў"), ("o`", "ў"), ("o‘", "ў"), ("oʻ", "ў"), ("o’", "ў"),
        ("g'", "ғ"), ("g`", "ғ"), ("g‘", "ғ"), ("gʻ", "ғ"), ("g’", "ғ"),

        ("A", "А"), ("B", "Б"), ("D", "Д"), ("E", "Е"), ("F", "Ф"),
        ("G", "Г"), ("H", "Ҳ"), ("I", "И"), ("J", "Ж"), ("K", "К"),
        ("L", "Л"), ("M", "М"), ("N", "Н"), ("O", "О"), ("P", "П"),
        ("Q", "Қ"), ("R", "Р"), ("S", "С"), ("T", "Т"), ("U", "У"),
        ("V", "В"), ("X", "Х"), ("Y", "Й"), ("Z", "З"),

        ("a", "а"), ("b", "б"), ("d", "д"), ("e", "е"), ("f", "ф"),
        ("g", "г"), ("h", "ҳ"), ("i", "и"), ("j", "ж"), ("k", "к"),
        ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"),
        ("q", "қ"), ("r", "р"), ("s", "с"), ("t", "т"), ("u", "у"),
        ("v", "в"), ("x", "х"), ("y", "й"), ("z", "з")
    ]

    placeholders = {}
    var_matches = set(re.findall(r'\{[a-zA-Z0-9_]+\}', text))
    for idx, var in enumerate(var_matches):
        p = f"\x02{idx}\x03"
        placeholders[p] = var
        text = text.replace(var, p)

    technical = ["COGS", "POS", "ERP", "HR", "CRM", "API", "ID", "USD", "UZS", "EUR", "URL", "QR", "JSON", "WS", "REST", "SKU"]
    for i, t in enumerate(technical):
        p = f"\x01{i}\x02"
        placeholders[p] = t
        text = text.replace(t, p)

    for lat, cyr in pairs:
        text = text.replace(lat, cyr)

    for p, t in placeholders.items():
        text = text.replace(p, t)

    return text

KNOWN_STRINGS = [
    # Analysis & Financials
    ("Oylik Moliyaviy Ko'rsatkichlar Jadvali", "monthlyFinancialTable", "Monthly Financial Indicators Table"),
    ("Hisobot Oyi", "reportMonth", "Report Month"),
    ("Jami Tushum ($)", "grossRevenueDollar", "Gross Revenue ($)"),
    ("Tannarx ($)", "cogsDollar", "COGS ($)"),
    ("Doimiy Oyliklar ($)", "permanentSalariesDollar", "Permanent Salaries ($)"),
    ("Qisqa Muddatli ($)", "shortTermDollar", "Short-term ($)"),
    ("Jami Xarajat ($)", "totalExpensesDollar", "Total Expenses ($)"),
    ("Haqiqiy Sof Foyda ($)", "netProfitDollar", "Real Net Profit ($)"),
    ("Rentabellik (%)", "marginPercent", "Profitability (%)"),
    ("Oylik Moliyaviy Yopilish va Savdolar Hisoboti", "monthlyClosingAndSalesTitle", "Monthly Financial Closing & Sales Report"),
    ("Tezkor tanlash:", "quickSelect", "Quick select:"),
    ("Davr:", "periodLabel", "Period:"),
    ("Amallar", "actions", "Actions"),
    ("Holati", "status", "Status"),
    ("Sana", "date", "Date"),
    ("Nomi", "name", "Name"),
    ("Telefon", "phone", "Phone"),
    ("Lavozim", "position", "Position"),
    ("Bo'lim", "department", "Department"),
    ("Kategoriya", "category", "Category"),
    ("Miqdori", "quantity", "Quantity"),
    ("Narxi", "price", "Price"),
    ("Jami", "total", "Total"),
    ("Qidirish", "search", "Search"),
    ("Tozalash", "reset", "Reset"),
    ("Saqlash", "save", "Save"),
    ("Yopish", "close", "Close"),
    ("Tahrirlash", "edit", "Edit"),
    ("O'chirish", "delete", "Delete"),
    ("Batafsil", "detail", "Details"),
    ("Tasdiqlash", "confirm", "Confirm"),
    ("Bekor qilish", "cancel", "Cancel"),
]

def run():
    print("Starting automated i18n extraction & mapping...")
    
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    erp_uz_entries = []
    erp_en_entries = []

    for uz_val, key, en_val in KNOWN_STRINGS:
        # Use json.dumps to safely escape single/double quotes!
        uz_quoted = json.dumps(uz_val, ensure_ascii=False)
        en_quoted = json.dumps(en_val, ensure_ascii=False)
        erp_uz_entries.append(f"    {key}: {uz_quoted},")
        erp_en_entries.append(f"    {key}: {en_quoted},")

    erp_uz_block = "  erp: {\n" + "\n".join(erp_uz_entries) + "\n  },"
    erp_en_block = "  erp: {\n" + "\n".join(erp_en_entries) + "\n  },"

    if "erp: {" in uz_text:
        uz_text = re.sub(r"  erp: \{[\s\S]*?\},", erp_uz_block, uz_text)
    else:
        uz_text = uz_text.replace("export default {", "export default {\n" + erp_uz_block)

    if "erp: {" in en_text:
        en_text = re.sub(r"  erp: \{[\s\S]*?\},", erp_en_block, en_text)
    else:
        en_text = en_text.replace("export default {", "export default {\n" + erp_en_block)

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_text)

    # Re-generate cr.ts safely
    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()
    print("Dictionaries updated cleanly with safe quotes!")

if __name__ == '__main__':
    run()
