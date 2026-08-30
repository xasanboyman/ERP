import os
import re
import json

NEW_KEYS = [
    ("heroSubtitle", "Bugun ERP tizimi orqali barcha jarayonlar va sotuvlarni nazorat qilishingiz mumkin.", "Control all processes and sales today through the ERP system."),
    ("activeTasks", "Faol Topshiriqlar", "Active Tasks"),
    ("totalVisits", "Kirishlar Soni", "Total Visits"),
    ("quickActions", "Tezkor Harakatlar", "Quick Actions"),
    ("quickActionsDesc", "Asosiy operatsiyalarga bir bosishda o'tish", "One-click access to core operations"),
    ("posSaleAction", "Yangi Sotuv (POS)", "New Sale (POS)"),
    ("posSaleDesc", "Kassa savdosi", "Cashier sale"),
    ("productsAction", "Mahsulotlar", "Products"),
    ("productsDesc", "Ombor va narxlar", "Warehouse and prices"),
    ("salaryAction", "Ish Haqi", "Salary"),
    ("salaryDesc", "Oylik to'lovlar", "Monthly payouts"),
    ("analyticsAction", "Analitika", "Analytics"),
    ("analyticsDesc", "Grafik va hisobot", "Charts and reports"),
    ("activeCountSuffix", "ta faol", "active"),
    ("allWorkers", "Barcha Xodimlar", "All Workers"),
    ("viewAll", "Barchasini ko'rish", "View all"),
    ("receiptDetail", "Chek Tafsiloti", "Receipt Details"),
    ("view", "Ko'rish", "View"),
    ("lowStockWarning", "Omborda Kam Qolgan Mahsulotlar", "Low Stock Products"),
    ("warningsCount", "ta ogohlantirish", "warnings"),
    ("unitsRemaining", "dona qoldi", "units left"),
]

def run():
    print("Enriching Workplace page translations...")
    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()
    with open(en_path, 'r', encoding='utf-8') as f:
        en_text = f.read()

    for k, uz_v, en_v in NEW_KEYS:
        uz_entry = f"    {k}: {json.dumps(uz_v, ensure_ascii=False)},"
        en_entry = f"    {k}: {json.dumps(en_v, ensure_ascii=False)},"
        if f"{k}:" not in uz_text:
            uz_text = uz_text.replace("erp: {", "erp: {\n" + uz_entry)
        if f"{k}:" not in en_text:
            en_text = en_text.replace("erp: {", "erp: {\n" + en_entry)

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_text)

    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()

    # Update Workplace.vue
    w_path = '/home/xasanboy/ERP/Front/src/views/Dashboard/Workplace.vue'
    with open(w_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(
        r'Bugun ERP tizimi orqali barcha jarayonlar va sotuvlarni nazorat qilishingiz\s*mumkin\.',
        '{{ t("erp.heroSubtitle") }}',
        content
    )
    content = content.replace('>Ombor Turlari<', '>{{ t("erp.productTypesCount") }}<')
    content = content.replace('>Faol Topshiriqlar<', '>{{ t("erp.activeTasks") }}<')
    content = content.replace('>Kirishlar Soni<', '>{{ t("erp.totalVisits") }}<')
    content = content.replace('Tezkor Harakatlar (ERP Quick Actions)', '{{ t("erp.quickActions") }}')
    content = content.replace("Asosiy operatsiyalarga bir bosishda o'tish", '{{ t("erp.quickActionsDesc") }}')
    content = content.replace('>Yangi Sotuv (POS)<', '>{{ t("erp.posSaleAction") }}<')
    content = content.replace('>Kassa checkout<', '>{{ t("erp.posSaleDesc") }}<')
    content = content.replace('>Mahsulotlar<', '>{{ t("erp.productsAction") }}<')
    content = content.replace('>Ombor va narxlar<', '>{{ t("erp.productsDesc") }}<')
    content = content.replace('>Ish Haqi<', '>{{ t("erp.salaryAction") }}<')
    content = content.replace('>Oylik to\'lovlar<', '>{{ t("erp.salaryDesc") }}<')
    content = content.replace('>Analitika<', '>{{ t("erp.analyticsAction") }}<')
    content = content.replace('>Grafik va hisobot<', '>{{ t("erp.analyticsDesc") }}<')
    content = content.replace('{{ activeWorkers.length }} ta faol', '{{ activeWorkers.length }} {{ t("erp.activeCountSuffix") }}')
    content = content.replace('Barcha Xodimlar', '{{ t("erp.allWorkers") }}')
    content = content.replace('Barchasini ko\'rish', '{{ t("erp.viewAll") }}')
    content = content.replace('Chek Tafsiloti', '{{ t("erp.receiptDetail") }}')
    content = content.replace('>Ko\'rish<', '>{{ t("erp.view") }}<')
    content = content.replace('Omborda Kam Qolgan Mahsulotlar', '{{ t("erp.lowStockWarning") }}')
    content = content.replace('{{ lowStockProducts.length }} ta ogohlantirish', '{{ lowStockProducts.length }} {{ t("erp.warningsCount") }}')
    content = content.replace('{{ prod.quantityInStock }} dona qoldi', '{{ prod.quantityInStock }} {{ t("erp.unitsRemaining") }}')

    with open(w_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Workplace.vue!")

if __name__ == '__main__':
    run()
