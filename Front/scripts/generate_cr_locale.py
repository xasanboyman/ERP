import re
import json

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

    # 1. Preserve curly brace variables like {percent}, {name}, {count}, etc.
    var_matches = set(re.findall(r'\{[a-zA-Z0-9_]+\}', text))
    for idx, var in enumerate(var_matches):
        p = f"\x02{idx}\x03"
        placeholders[p] = var
        text = text.replace(var, p)

    # 2. Preserve technical acronyms
    technical = ["COGS", "POS", "ERP", "HR", "CRM", "API", "ID", "USD", "UZS", "EUR", "URL", "QR", "JSON", "WS", "REST", "SKU"]
    for i, t in enumerate(technical):
        p = f"\x01{i}\x02"
        placeholders[p] = t
        text = text.replace(t, p)

    # 3. Transliterate
    for lat, cyr in pairs:
        text = text.replace(lat, cyr)

    # 4. Restore preserved variables & technical tokens
    for p, t in placeholders.items():
        text = text.replace(p, t)

    return text

def convert_uz_to_cr():
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    cr_path = '/home/xasanboy/ERP/Front/src/locales/cr.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_content = f.read()

    # Match string values inside uz.ts: key: 'Value' or key: "Value"
    def replacer(match):
        prefix = match.group(1) # e.g. "key: '"
        val = match.group(2)    # e.g. "Matn"
        suffix = match.group(3) # e.g. "',"
        cyr_val = latin_to_cyrillic(val)
        return f"{prefix}{cyr_val}{suffix}"

    # Replace values in single quotes
    cr_content = re.sub(r"([a-zA-Z0-9_]+:\s*')([^']*)(')", replacer, uz_content)
    # Replace values in double quotes
    cr_content = re.sub(r'([a-zA-Z0-9_]+:\s*")([^"]*)(")', replacer, cr_content)

    with open(cr_path, 'w', encoding='utf-8') as f:
        f.write(cr_content)

    print("Successfully generated src/locales/cr.ts from uz.ts")

if __name__ == '__main__':
    convert_uz_to_cr()
