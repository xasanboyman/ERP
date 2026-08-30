#!/usr/bin/env python3
"""
Convert all hardcoded text in Workplace.vue to reactive t('...') i18n calls.
"""

filepath = '/home/xasanboy/ERP/Front/src/views/Dashboard/Workplace.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

REPLACEMENTS = [
    # Script defaults
    ("customer_name: 'Мижоз'", "customer_name: t('workplace.customerColon').replace(':', '')"),
    ("product_name: log.entityName || 'Сотув операцияси'", "product_name: log.entityName || t('workplace.saleOperationDefault')"),
    ("worker.role || 'Ходим'", "worker.role || t('workplace.defaultWorkerRole')"),
    
    # Template
    ("✓ Барча маҳсулотлар етарли миқдорда мавжуд", "{{ t('workplace.allProductsSufficient') }}"),
    ("<span class=\"text-12px text-gray-400\">Топ сотувлар</span>", "<span class=\"text-12px text-gray-400\">{{ t('workplace.topSales') }}</span>"),
    ("Омборда: {{ formatMoney(product.quantityInStock) }} дона", "{{ t('workplace.inStockCount', { qty: formatMoney(product.quantityInStock) }) }}"),
    
    # Activity modal
    ("title=\"Барча Фаолликлар ва Ҳаракатлар Журнали (Аудит Траил)\"", ":title=\"t('workplace.auditTrailTitle')\""),
    ("<ElRadioButton value=\"sales\">Сотув & Чеклар</ElRadioButton>", "<ElRadioButton value=\"sales\">{{ t('workplace.salesReceiptsTab') }}</ElRadioButton>"),
    ("<ElRadioButton value=\"worker\">Ходимлар</ElRadioButton>", "<ElRadioButton value=\"worker\">{{ t('erp.allWorkers') }}</ElRadioButton>"),
    ("placeholder=\"Фойдаланувчи, Чек # ёки объект излаш...\"", ":placeholder=\"t('workplace.searchAuditPlaceholder')\""),
    ("label=\"Вақт\"", ":label=\"t('workplace.timeColumn')\""),
    ("label=\"Фойдаланувчи\"", ":label=\"t('workplace.userColumn')\""),
    ("label=\"Ҳаракат Тури\"", ":label=\"t('workplace.actionTypeColumn')\""),
    ("label=\"Операция Тафсилоти ва Чек\"", ":label=\"t('workplace.operationDetailColumn')\""),
    ("label=\"Амал\"", ":label=\"t('workplace.actionColumn')\""),
    ("> Тафсилот", "> {{ t('workplace.detailAction') }}"),
    ("Жами фаолликлар сони: {{ filteredFullActivities.length }} та", "{{ t('workplace.totalActivitiesCount', { count: filteredFullActivities.length }) }}"),
    
    # Receipt modal
    ("title=\"Чек ва Операция Тафсилотлари\"", ":title=\"t('workplace.receiptDetailsTitle')\""),
    ("{{ receiptData.receipt_number || 'СОТУВ ЧЕКИ' }}", "{{ receiptData.receipt_number || t('workplace.salesReceiptUpper') }}"),
    ("Сана:", "{{ t('workplace.dateLabelColon') }}"),
    ("{{ receiptData.payment_method === 'nasiya' ? 'НАСИЯ ҚАРЗ' : \"ТЎЛАНГАН\" }}", "{{ receiptData.payment_method === 'nasiya' ? t('workplace.nasiyaDebtUpper') : t('workplace.paidSuccessUpper') }}"),
    ("<span class=\"text-12px text-gray-400\">Кассир:</span>", "<span class=\"text-12px text-gray-400\">{{ t('workplace.cashierColon') }}</span>"),
    ("<span class=\"text-12px text-gray-400\">Мижоз:</span>", "<span class=\"text-12px text-gray-400\">{{ t('workplace.customerColon') }}</span>"),
    ("{{ receiptData.customer_name || 'Оддий харидор' }}", "{{ receiptData.customer_name || t('workplace.defaultBuyer') }}"),
    ("Сотиб Олинган Маҳсулотлар Рўйхати", "{{ t('workplace.purchasedProductsList') }}"),
    ("label=\"Нархи ($)\"", ":label=\"t('analysis.priceDollar')\""),
    ("label=\"Сони\"", ":label=\"t('workplace.qtyHeader')\""),
    ("label=\"Жами ($)\"", ":label=\"t('analysis.totalDollar')\""),
    ("Умумий Сумма:", "{{ t('workplace.totalSumColon') }}"),
    ("Тўланган Пул:", "{{ t('workplace.paidMoneyColon') }}"),
    (">Қарз Суммаси:<", ">{{ t('workplace.debtSumColon') }}<"),
    ("Чек маълумотлари топилмади", "{{ t('workplace.receiptNotFound') }}"),
    (">Тушунарли<", ">{{ t('workplace.understoodBtn') }}<"),
]

count = 0
for old, new in REPLACEMENTS:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  ✓ Replaced: {old[:50]}...")
    else:
        print(f"  ⚠ Not found: {old[:50]}...")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total replacements applied in Workplace.vue: {count}")
