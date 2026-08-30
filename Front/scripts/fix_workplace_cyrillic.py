#!/usr/bin/env python3
"""
Translate Latin Uzbek text in Workplace.vue to Cyrillic.
"""

filepath = '/home/xasanboy/ERP/Front/src/views/Dashboard/Workplace.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

REPLACEMENTS = [
    # JavaScript defaults
    ("customer_name: 'Mijoz'", "customer_name: 'Мижоз'"),
    ("product_name: log.entityName || 'Sotuv operatsiyasi'", "product_name: log.entityName || 'Сотув операцияси'"),
    ("worker.role || 'Xodim'", "worker.role || 'Ходим'"),
    
    # Low stock alert
    ("✓ Barcha mahsulotlar yetarli miqdorda mavjud", "✓ Барча маҳсулотлар етарли миқдорда мавжуд"),
    
    # Top sales
    ("<span class=\"text-12px text-gray-400\">Top sotuvlar</span>", "<span class=\"text-12px text-gray-400\">Топ сотувлар</span>"),
    ("Omborda: {{ formatMoney(product.quantityInStock) }} dona", "Омборда: {{ formatMoney(product.quantityInStock) }} дона"),
    
    # Activity log modal
    ("title=\"Barcha Faolliklar va Harakatlar Jurnali (Audit Trail)\"", "title=\"Барча Фаолликлар ва Ҳаракатлар Журнали (Аудит Траил)\""),
    ("<ElRadioButton value=\"sales\">Sotuv & Cheklar</ElRadioButton>", "<ElRadioButton value=\"sales\">Сотув & Чеклар</ElRadioButton>"),
    ("<ElRadioButton value=\"worker\">Xodimlar</ElRadioButton>", "<ElRadioButton value=\"worker\">Ходимлар</ElRadioButton>"),
    ("placeholder=\"Foydalanuvchi, Chek # yoki obyekt izlash...\"", "placeholder=\"Фойдаланувчи, Чек # ёки объект излаш...\""),
    ("label=\"Vaqt\"", "label=\"Вақт\""),
    ("label=\"Foydalanuvchi\"", "label=\"Фойдаланувчи\""),
    ("label=\"Harakat Turi\"", "label=\"Ҳаракат Тури\""),
    ("label=\"Operatsiya Tafsiloti va Chek\"", "label=\"Операция Тафсилоти ва Чек\""),
    ("label=\"Amal\"", "label=\"Амал\""),
    ("> Tafsilot", "> Тафсилот"),
    ("Jami faolliklar soni: {{ filteredFullActivities.length }} ta", "Жами фаолликлар сони: {{ filteredFullActivities.length }} та"),
    
    # Receipt detail modal
    ("title=\"Chek va Operatsiya Tafsilotlari\"", "title=\"Чек ва Операция Тафсилотлари\""),
    ("{{ receiptData.receipt_number || 'SOTUV CHEKI' }}", "{{ receiptData.receipt_number || 'СОТУВ ЧЕКИ' }}"),
    ("Sana:", "Сана:"),
    ("{{ receiptData.payment_method === 'nasiya' ? 'NASIYA QARZ' : \"TO'LANGAN\" }}", "{{ receiptData.payment_method === 'nasiya' ? 'НАСИЯ ҚАРЗ' : \"ТЎЛАНГАН\" }}"),
    ("<span class=\"text-12px text-gray-400\">Kassir:</span>", "<span class=\"text-12px text-gray-400\">Кассир:</span>"),
    ("<span class=\"text-12px text-gray-400\">Mijoz:</span>", "<span class=\"text-12px text-gray-400\">Мижоз:</span>"),
    ("{{ receiptData.customer_name || 'Oddiy xaridor' }}", "{{ receiptData.customer_name || 'Оддий харидор' }}"),
    ("Sotib Olingan Mahsulotlar Ro'yxati", "Сотиб Олинган Маҳсулотлар Рўйхати"),
    ("label=\"Narxi ($)\"", "label=\"Нархи ($)\""),
    ("label=\"Soni\"", "label=\"Сони\""),
    ("label=\"Jami ($)\"", "label=\"Жами ($)\""),
    ("Umumiy Summa:", "Умумий Сумма:"),
    ("To'langan Pul:", "Тўланган Пул:"),
    (">Qarz Summasi:<", ">Қарз Суммаси:<"),
    ("Chek ma'lumotlari topilmadi", "Чек маълумотлари топилмади"),
    (">Tushunarli<", ">Тушунарли<"),
]

count = 0
for old, new in REPLACEMENTS:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  ✓ Replaced: {old[:50]}...")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total replacements applied in Workplace.vue: {count}")
