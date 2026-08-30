import os
import re

def latin_to_cyrillic(text: str) -> str:
    if not text or not isinstance(text, str):
        return text

    # Multi-character rules first (Order is critical!)
    pairs = [
        # Diphthongs & apostrophe letters
        ("Sh", "Ш"), ("SH", "Ш"), ("Ch", "Ч"), ("CH", "Ч"),
        ("Yo", "Ё"), ("YO", "Ё"), ("Yu", "Ю"), ("YU", "Ю"),
        ("Ya", "Я"), ("YA", "Я"), ("Ye", "Е"), ("YE", "Е"),
        ("O'", "Ў"), ("O`", "Ў"), ("O‘", "Ў"), ("Oʻ", "Ў"), ("O’", "Ў"),
        ("G'", "Ғ"), ("G`", "Ғ"), ("G‘", "Ғ"), ("Gʻ", "Ғ"), ("G’", "Ғ"),

        ("sh", "ш"), ("ch", "ч"), ("yo", "ё"), ("yu", "ю"),
        ("ya", "я"), ("ye", "е"),
        ("o'", "ў"), ("o`", "ў"), ("o‘", "ў"), ("oʻ", "ў"), ("o’", "ў"),
        ("g'", "ғ"), ("g`", "ғ"), ("g‘", "ғ"), ("gʻ", "ғ"), ("g’", "ғ"),

        # Single uppercase
        ("A", "А"), ("B", "Б"), ("D", "Д"), ("E", "Е"), ("F", "Ф"),
        ("G", "Г"), ("H", "Ҳ"), ("I", "И"), ("J", "Ж"), ("K", "К"),
        ("L", "Л"), ("M", "М"), ("N", "Н"), ("O", "О"), ("P", "П"),
        ("Q", "Қ"), ("R", "Р"), ("S", "С"), ("T", "Т"), ("U", "У"),
        ("V", "В"), ("X", "Х"), ("Y", "Й"), ("Z", "З"),

        # Single lowercase
        ("a", "а"), ("b", "б"), ("d", "д"), ("e", "е"), ("f", "ф"),
        ("g", "г"), ("h", "ҳ"), ("i", "и"), ("j", "ж"), ("k", "к"),
        ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"),
        ("q", "қ"), ("r", "р"), ("s", "с"), ("t", "т"), ("u", "у"),
        ("v", "в"), ("x", "х"), ("y", "й"), ("z", "з")
    ]

    # Technical acronyms that should stay in Latin
    technical = ["COGS", "POS", "ERP", "HR", "CRM", "API", "ID", "USD", "UZS", "URL", "QR", "JSON", "WS", "REST", "SKU"]
    placeholders = {}
    for i, t in enumerate(technical):
        p = f"\x01{i}\x02"
        placeholders[p] = t
        text = text.replace(t, p)

    for lat, cyr in pairs:
        text = text.replace(lat, cyr)

    for p, t in placeholders.items():
        text = text.replace(p, t)

    return text

if __name__ == "__main__":
    test_phrases = [
        "Standart Moliyaviy Tahlil",
        "Oylik Yopilish & Tarixiy Arxiv",
        "Davrlarni Taqqoslash (Delta)",
        "JAMI TUSHUM (GROSS REVENUE)",
        "MAHSULOT TANNARXI (COGS)",
        "JAMI ISH HAQI XARAJATI",
        "HAQIQIY SOF FOYDA",
        "Savdolar va Aylanma",
        "Doimiy Xodimlar Maoshi",
        "Qisqa Muddatli Ishchilar",
        "Kategoriyalar Bo'yicha Tushum va Sof Foyda"
    ]
    for p in test_phrases:
        print(f"{p:45} -> {latin_to_cyrillic(p)}")
