#!/usr/bin/env python3
"""
Comprehensive script to translate ALL Latin Uzbek text in Analysis.vue to Cyrillic.
"""

filepath = '/home/xasanboy/ERP/Front/src/views/Dashboard/Analysis.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Ordered replacements - longer/more specific strings first to avoid partial matches
REPLACEMENTS = [
    # ===== SCRIPT SECTION =====
    
    # Line 64-65: Period labels (initial values)
    ("period1Label = ref('Avgust 2026 (Ushbu oy)')", "period1Label = ref('Август 2026 (Ушбу ой)')"),
    ("period2Label = ref('Iyul 2026 (O\u2019tgan oy)')", "period2Label = ref('Июл 2026 (Ўтган ой)')"),
    # Handle alternate quote style
    ("period2Label = ref('Iyul 2026 (O'tgan oy)')", "period2Label = ref('Июл 2026 (Ўтган ой)')"),
    
    # Line 154-164: Quick jump months
    ("label: 'Joriy Oy (Avgust)'", "label: 'Жорий Ой (Август)'"),
    ("tip: \"2026-08 oyi tushumi va joriy oydagi savdolarni ko'rish\"", "tip: '2026-08 ойи тушуми ва жорий ойдаги савдоларни кўриш'"),
    ("label: \"O'tgan Oy (Iyul)\"", "label: 'Ўтган Ой (Июл)'"),
    ("tip: \"2026-07 oyi yakuniy hisobotini ko'rish yoki muhrlash\"", "tip: '2026-07 ойи якуний ҳисоботини кўриш ёки муҳрлаш'"),
    ("label: 'Iyun 2026'", "label: 'Июн 2026'"),
    ("tip: \"2026-06 oyi arxiv va savdo ko'rsatkichlari\"", "tip: '2026-06 ойи архив ва савдо кўрсаткичлари'"),
    ("label: 'May 2026'", "label: 'Май 2026'"),
    ("tip: \"2026-05 oyi arxiv va savdo ko'rsatkichlari\"", "tip: '2026-05 ойи архив ва савдо кўрсаткичлари'"),
    
    # Line 309: Warning message
    ("'Iltimos, hisobot oyini tanlang!'", "'Илтимос, ҳисобот ойини танланг!'"),
    
    # Line 314: Confirm dialog - the big template literal
    ("`Haqiqatan ham <b>${month}</b> oyi moliyaviy hisobotini yopish va tarixga muhrlashni xohlaysizmi?<br/><br/><small class=\"text-gray-500\">* Yopilgandan so'ng natijalar doimiy arxivga saqlanadi va yangi oy hisoblagichlari yangidan ishga tushadi.</small>`",
     "`Ҳақиқатан ҳам <b>${month}</b> ойи молиявий ҳисоботини ёпиш ва тарихга муҳрлашни хоҳлайсизми?<br/><br/><small class=\"text-gray-500\">* Ёпилгандан сўнг натижалар доимий архивга сақланади ва янги ой ҳисоблагичлари янгидан ишга тушади.</small>`"),
    ("'Oylik Hisobotni Muhrlash'", "'Ойлик Ҳисоботни Муҳрлаш'"),
    ("'Ha, Muhrlash va Saqlash'", "'Ҳа, Муҳрлаш ва Сақлаш'"),
    ("'Bekor qilish'", "'Бекор қилиш'"),
    ("'Hisobotni yopishda xatolik yuz berdi'", "'Ҳисоботни ёпишда хатолик юз берди'"),
    
    # Line 328: Remark template
    ("`${month} oyi yakuniy moliyaviy hisoboti (Yopildi)`", "`${month} ойи якуний молиявий ҳисоботи (Ёпилди)`"),
    # Line 332: Success message
    ("`${month} oyi moliyaviy hisoboti muvaffaqiyatli yopildi!`", "`${month} ойи молиявий ҳисоботи муваффақиятли ёпилди!`"),
    
    # Line 351: Delete confirm
    ("`<b>${row.period_month}</b> oyi arxiv hisobotini o'chirishni tasdiqlaysizmi?`", "`<b>${row.period_month}</b> ойи архив ҳисоботини ўчиришни тасдиқлайсизми?`"),
    ("\"Tarixni o'chirish\"", "'Тарихни ўчириш'"),
    ("\"O'chirish\"", "'Ўчириш'"),
    ("\"Arxivdan o'chirildi\"", "'Архивдан ўчирилди'"),
    
    # Line 391: Donut chart series names
    ("name: 'Mahsulot Tannarxi (COGS)'", "name: 'Маҳсулот Таннархи (COGS)'"),
    ("name: `Doimiy ${t('erp.salaries')} & Avanslar`", "name: `Доимий ${t('erp.salaries')} & Авансlар`"),
    ("name: 'Qisqa Muddatli Ishchilar'", "name: 'Қисқа Муддатли Ишчилар'"),
    
    # Line 478: Pie series name
    ("name: 'Moliyaviy Taqsimot'", "name: 'Молиявий Тақсимот'"),
    
    # Line 508: Month names array
    ("const months = ['Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust']",
     "const months = ['Март', 'Апрел', 'Май', 'Июн', 'Июл', 'Август']"),
    
    # Line 643-670: Comparison period labels
    ("period1Label.value = 'Avgust 2026 (Ushbu oy)'", "period1Label.value = 'Август 2026 (Ушбу ой)'"),
    ("period2Label.value = 'Iyul 2026 (O\u2019tgan oy)'", "period2Label.value = 'Июл 2026 (Ўтган ой)'"),
    ("period2Label.value = 'Iyul 2026 (O'tgan oy)'", "period2Label.value = 'Июл 2026 (Ўтган ой)'"),
    ("period1Label.value = '3-Chorak 2026 (Q3)'", "period1Label.value = '3-Чорак 2026 (Q3)'"),
    ("period2Label.value = '2-Chorak 2026 (Q2)'", "period2Label.value = '2-Чорак 2026 (Q2)'"),
    ("period1Label.value = 'Oxirgi 30 kun'", "period1Label.value = 'Охирги 30 кун'"),
    ("period2Label.value = 'Oldingi 30 kun'", "period2Label.value = 'Олдинги 30 кун'"),
    ("period1Label.value = '2026 Yillik natijalar'", "period1Label.value = '2026 Йиллик натижалар'"),
    ("period2Label.value = '2025 Yillik natijalar'", "period2Label.value = '2025 Йиллик натижалар'"),
    (": '1-Davr'", ": '1-Давр'"),
    (": '2-Davr'", ": '2-Давр'"),
    ("period1Label.value = `1-Davr (${p1Text})`", "period1Label.value = `1-Давр (${p1Text})`"),
    ("period2Label.value = `2-Davr (${p2Text})`", "period2Label.value = `2-Давр (${p2Text})`"),
    
    # Line 736-810: Comparison table metric rows
    ("metric: 'Jami Tushum (Gross Revenue)'", "metric: 'Жами Тушум (Gross Revenue)'"),
    ("desc: 'Barcha sotilgan tovarlardan tushgan yalpi daromad'", "desc: 'Барча сотилган товарлардан тушган ялпи даромад'"),
    ("\"Sotuvlar orqali korxonaga kirgan umumiy summa. Qancha yuqori bo'lsa, savdo hajmi shuncha yaxshi.\"",
     "'Сотувлар орқали корхонага кирган умумий сумма. Қанча юқори бўлса, савдо ҳажми шунча яхши.'"),
    
    ("metric: 'Mahsulot Tannarxi (COGS)'", "metric: 'Маҳсулот Таннархи (COGS)'"),
    ("desc: 'Sotilgan tovarlarning asl xarid va tayyorlash qiymati'", "desc: 'Сотилган товарларнинг асл харид ва тайёрлаш қиймати'"),
    ("\"Mahsulotlarni omborga olib kelish yoki ishlab chiqarish uchun sarflangan to'g'ridan-to'g'ri xarajat.\"",
     "'Маҳсулотларни омборга олиб келиш ёки ишлаб чиқариш учун сарфланган тўғридан-тўғри харажат.'"),
    
    ("metric: 'Doimiy Ishchilar Maoshi (Staff Salaries)'", "metric: 'Доимий Ишчилар Маоши (Staff Salaries)'"),
    ("desc: 'Doimiy shtatdagi xodimlarning belgilangan tarif oyliklari'", "desc: 'Доимий штатдаги ходимларнинг белгиланган тариф ойликлари'"),
    ("\"Har oy xodimlarga to'lanadigan qat'iy belgilangan asosiy oylik maoshlar yig'indisi.\"",
     "'Ҳар ой ходимларга тўланадиган қатъий белгиланган асосий ойлик маошлар йиғиндиси.'"),
    
    ("metric: 'Qisqa Muddatli Ishchilar (Piece-rate / Vyrabotka)'", "metric: 'Қисқа Муддатли Ишчилар (Piece-rate / Выработка)'"),
    ("desc: \"Hosil yoki bajarilgan ish hajmi bo'yicha to'langan ish haqi\"", "desc: 'Ҳосил ёки бажарилган иш ҳажми бўйича тўланган иш ҳақи'"),
    ("\"Vaqtincha yoki donabay (vyrabotka) ishchilar bajargan hajmlariga qarab olgan to'lovlar.\"",
     "'Вақтинча ёки донабай (выработка) ишчилар бажарган ҳажмларига қараб олган тўловлар.'"),
    
    ("metric: 'Jami Ish Haqi Xarajatlari (Total Payroll)'", "metric: 'Жами Иш Ҳақи Харажатлари (Total Payroll)'"),
    ("desc: \"Kompaniyaning barcha oylik to'lovlari yig'indisi\"", "desc: 'Компаниянинг барча ойлик тўловлари йиғиндиси'"),
    ("\"Doimiy oyliklar va qo'shimcha ish hajmi uchun to'langan barcha mehnat xarajatlari summasi.\"",
     "'Доимий ойликлар ва қўшимча иш ҳажми учун тўланган барча меҳнат харажатлари суммаси.'"),
    
    ("desc: 'Tannarx va barcha oyliklar chegirilgan toza foyda'", "desc: 'Таннарх ва барча ойликлар чегирилган тоза фойда'"),
    ("\"Kompaniyaning barcha xarajatlaridan keyin toza cho'ntagiga qolgan haqiqiy daromad.\"",
     "'Компаниянинг барча харажатларидан кейин тоза чўнтагига қолган ҳақиқий даромад.'"),
    
    ("metric: 'Rentabellik Marjasi (Profit Margin %)'", "metric: 'Рентабеллик Маржаси (Profit Margin %)'"),
    ("desc: 'Sof foydaning umumiy tushumdagi foiz ulushi'", "desc: 'Соф фойданинг умумий тушумдаги фоиз улуши'"),
    ("\"Har $100 dollarlik savdodan kompaniyaga necha dollar sof foyda qolayotganini ko'rsatuvchi samaradorlik indeksi.\"",
     "'Ҳар $100 долларлик савдодан компанияга неча доллар соф фойда қолаётганини кўрсатувчи самарадорлик индекси.'"),
    
    # Line 825: Chart categories
    ("'Jami Tushum'", "'Жами Тушум'"),
    ("'Ish Haqi'", "'Иш Ҳақи'"),
    
    # Line 976, 981: Comparison donut labels
    ("name: 'Ish Haqi (Payroll)'", "name: 'Иш Ҳақи (Payroll)'"),
    ("name: 'Sof Foyda (Profit)'", "name: 'Соф Фойда (Profit)'"),
    
    # ===== TEMPLATE SECTION =====
    
    # Tooltip contents (long strings first)
    ('content="Kompaniyaning umumiy moliyaviy oqimlari, oylik dinamika va kategoriyalar bo\'yicha rentabellik ko\'rinishi"',
     'content="Компаниянинг умумий молиявий оқимлари, ойлик динамика ва категориялар бўйича рентабеллик кўриниши"'),
    ('content="Har bir oyni rasmiy yopish, sof foydani muzlatish, o\'sha oydagi barcha savdo cheklari va arxivlangan hisobotlar"',
     'content="Ҳар бир ойни расмий ёпиш, соф фойдани музлатиш, ўша ойдаги барча савдо чеклари ва архивланган ҳисоботлар"'),
    ('content="Ikki davr (joriy oy va o\'tgan oy, yoki choraklar) o\'rtasidagi daromad, xarajat, oyliklar va sof foydaning mutlaq va foiz o\'zgarishi (Delta) tahlili"',
     'content="Икки давр (жорий ой ва ўтган ой, ёки чораклар) ўртасидаги даромад, харажат, ойликлар ва соф фойданинг мутлақ ва фоиз ўзгариши (Делта) таҳлили"'),
    ('content="Barcha savdo, xodimlar, ombor va moliyaviy ma\'lumotlarni bazadan qayta yuklash"',
     'content="Барча савдо, ходимлар, омбор ва молиявий маълумотларни базадан қайта юклаш"'),
    ('content="Oxirgi 6 oy davomida tushum, tannarx, oyliklar va haqiqiy sof foydaning o\'zgarish chiziqlari"',
     'content="Охирги 6 ой давомида тушум, таннарх, ойликлар ва ҳақиқий соф фойданинг ўзгариш чизиқлари"'),
    ('content="Jami xarajatlarning qaysi qismi mahsulot tannarxiga, qaysi qismi ish haqiga to\'g\'ri kelishining foiz taqsimoti"',
     'content="Жами харажатларнинг қайси қисми маҳсулот таннархига, қайси қисми иш ҳақига тўғри келишининг фоиз тақсимоти"'),
    ('content="Mahsulot toifalari (kategoriyalar) bo\'yicha jami savdo summasi va ulardan qolgan sof foyda"',
     'content="Маҳсулот тоифалари (категориялар) бўйича жами савдо суммаси ва улардан қолган соф фойда"'),
    ('content="Har bir oyning tushumi, tannarxi, oylik xarajatlari, jami xarajat va hisoblangan rentabellik foizi"',
     'content="Ҳар бир ойнинг тушуми, таннархи, ойлик харажатлари, жами харажат ва ҳисобланган рентабеллик фоизи"'),
    ('content="Qaysi oyning moliyaviy hisobotini ko\'rish yoki yopishni xohlasangiz, shu oyni tanlang"',
     'content="Қайси ойнинг молиявий ҳисоботини кўриш ёки ёпишни хоҳласангиз, шу ойни танланг"'),
    ('content="Tanlangan oyda amalga oshirilgan barcha savdo cheklaridan tushgan umumiy yalpi summa"',
     'content="Танланган ойда амалга оширилган барча савдо чекларидан тушган умумий ялпи сумма"'),
    ('content="Sotilgan barcha tovarlarning asl xarid yoki ishlab chiqarish tannarxi (COGS)"',
     'content="Сотилган барча товарларнинг асл харид ёки ишлаб чиқариш таннархи (COGS)"'),
    ("content=\"Xodimlarga to'lanadigan doimiy tarif oyliklari va qisqa muddatli (vyrabotka) ish hajmi to'lovlari summasi\"",
     'content="Ходимларга тўланадиган доимий тариф ойликлари ва қисқа муддатли (выработка) иш ҳажми тўловлари суммаси"'),
    ("content=\"Barcha mahsulot tannarxi va xodimlar ish haqi xarajatlari to'liq chegirilgandan keyin qolgan sof foyda\"",
     'content="Барча маҳсулот таннархи ва ходимлар иш ҳақи харажатлари тўлиқ чегирилгандан кейин қолган соф фойда"'),
    ('content="Ushbu oyda qilingan har bir $100 dollar daromadning tannarx, oyliklar va sof foydaga taqsimlanish halqasi"',
     'content="Ушбу ойда қилинган ҳар бир $100 доллар даромаднинг таннарх, ойликлар ва соф фойдага тақсимланиш ҳалқаси"'),
    ("content=\"Oxirgi 6 oy davomida tushum, xarajatlar va sof foydaning uzluksiz o'sish egri chiziqlari\"",
     'content="Охирги 6 ой давомида тушум, харажатлар ва соф фойданинг узлуксиз ўсиш эгри чизиқлари"'),
    ("content=\"Tanlangan oyda ro'y bergan barcha savdo operatsiyalari va cheklar ro'yxati\"",
     'content="Танланган ойда рўй берган барча савдо операциялари ва чеклар рўйхати"'),
    ('content="Oldingi yopilgan va muhrlangan barcha oylarning rasmiy arxiv jadvallari"',
     'content="Олдинги ёпилган ва муҳрланган барча ойларнинг расмий архив жадваллари"'),
    ("content=\"Tanlangan oy bo'yicha barcha cheklarning umumiy yig'indisi\"",
     'content="Танланган ой бўйича барча чекларнинг умумий йиғиндиси"'),
    ("content=\"Mijozlar tomonidan amalda to'lab berilgan summa\"",
     'content="Мижозлар томонидан амалда тўлаб берилган сумма"'),
    ('content="Nasiya / qarzga olingan tovarlar summasi"',
     'content="Насия / қарзга олинган товарлар суммаси"'),
    ("content=\"Savdo ma'lumotlarini yangilash\"",
     'content="Савдо маълумотларини янгилаш"'),
    ('content="Arxivdagi barcha oylarni qayta yuklash"',
     'content="Архивдаги барча ойларни қайта юклаш"'),
    ("content=\"Chek raqami, mijoz ismi, telefon raqami yoki kassir bo'yicha qidirish\"",
     'content="Чек рақами, мижоз исми, телефон рақами ёки кассир бўйича қидириш"'),
    ("content=\"To'lov turi bo'yicha filtrlash (Naqd, Karta, Nasiya, O'tkazma)\"",
     'content="Тўлов тури бўйича фильтрлаш (Нақд, Карта, Насия, Ўтказма)"'),
    ('content="Noyob tranzaksiya / chek kodi"',
     'content="Ноёб транзакция / чек коди"'),
    ("content=\"Chek ichidagi barcha tovarlar ro'yxati, narxlari va miqdorini ko'rish\"",
     'content="Чек ичидаги барча товарлар рўйхати, нархлари ва миқдорини кўриш"'),
    ("content=\"Ushbu oyning rasmiy muhrlangan sertifikatini ko'rish\"",
     'content="Ушбу ойнинг расмий муҳрланган сертификатини кўриш"'),
    ("content=\"Ushbu oylik arxiv hisobotini bazadan o'chirish\"",
     'content="Ушбу ойлик архив ҳисоботини базадан ўчириш"'),
    # Comparison tooltips
    ("content=\"Oyma-oy (Month-over-Month): Ushbu oyni o'tgan oy bilan taqqoslash (Avgust vs Iyul)\"",
     'content="Ойма-ой (Month-over-Month): Ушбу ойни ўтган ой билан таққослаш (Август vs Июл)"'),
    ("content=\"Chorakma-chorak (Quarter-over-Quarter): Joriy 3 oylik chorakni o'tgan chorak bilan taqqoslash\"",
     'content="Чоракма-чорак (Quarter-over-Quarter): Жорий 3 ойлик чоракни ўтган чорак билан таққослаш"'),
    ('content="Oxirgi 30 kunlik faoliyatni undan oldingi 30 kunlik davr bilan solishtirish"',
     'content="Охирги 30 кунлик фаолиятни ундан олдинги 30 кунлик давр билан солиштириш"'),
    ("content=\"Yillik (Year-over-Year): Bu yilgi natijalarni o'tgan yilgi xuddi shu davr bilan taqqoslash\"",
     'content="Йиллик (Year-over-Year): Бу йилги натижаларни ўтган йилги худди шу давр билан таққослаш"'),
    ("content=\"Ixtiyoriy 2 ta sana oralig'ini o'zingiz tanlab taqqoslang\"",
     'content="Ихтиёрий 2 та сана оралиғини ўзингиз танлаб таққосланг"'),
    ("content=\"1-Davr va 2-Davrdagi barcha sotuvlardan tushgan umumiy tushum farqi (Delta). Musbat bo'lsa savdo o'sganini bildiradi.\"",
     'content="1-Давр ва 2-Даврдаги барча сотувлардан тушган умумий тушум фарқи (Делта). Мусбат бўлса савдо ўсганини билдиради."'),
    ("content=\"Sotilgan tovarlar tannarxining davrlar orasidagi farqi. Tovar tannarxi o'sishi yoki tejalganini ko'rsatadi.\"",
     'content="Сотилган товарлар таннархининг давлар орасидаги фарқи. Товар таннархи ўсиши ёки тежалганини кўрсатади."'),
    ("content=\"Xodimlarning barcha oylik maoshlari va qo'shimcha to'lovlarining davrlar orasidagi o'zgarishi.\"",
     'content="Ходимларнинг барча ойлик маошлари ва қўшимча тўловларининг давлар орасидаги ўзгариши."'),
    ("content=\"Barcha tannarx va oyliklar chegirilgandan keyin qolgan sof daromadning o'sishi yoki kamayishi (Haqiqiy biznes natijasi).\"",
     'content="Барча таннарх ва ойликлар чегирилгандан кейин қолган соф даромаднинг ўсиши ёки камайиши (Ҳақиқий бизнес натижаси)."'),
    ("content=\"1-Davr va 2-Davrning har bir asosiy ko'rsatkichini yonma-yon solishtirib beruvchi ustunli grafik\"",
     'content="1-Давр ва 2-Даврнинг ҳар бир асосий кўрсаткичини ёнма-ён солиштириб берувчи устунли график"'),
    ("content=\"1-Davrda topilgan umumiy daromad qaysi yo'nalishlarga (tannarx, oyliklar, sof foyda) qanday foizda taqsimlanganini ko'rsatadi\"",
     'content="1-Даврда топилган умумий даромад қайси йўналишларга (таннарх, ойликлар, соф фойда) қандай фоизда тақсимланганини кўрсатади"'),
    ("content=\"Har bir moliyaviy ko'rsatkichning 1-davr va 2-davrdagi aniq summalari, ularning ayirmasi (Delta) va foizdagi o'zgarish sur'ati\"",
     'content="Ҳар бир молиявий кўрсаткичнинг 1-давр ва 2-давридаги аниқ суммалари, уларнинг айирмаси (Делта) ва фоиздаги ўзгариш суръати"'),
    ("content=\"1-Davr (asosiy davr) bo'yicha hisoblangan summa\"",
     'content="1-Давр (асосий давр) бўйича ҳисобланган сумма"'),
    ("content=\"2-Davr (taqqoslanayotgan davr) bo'yicha hisoblangan summa\"",
     'content="2-Давр (таққосланаётган давр) бўйича ҳисобланган сумма"'),
    ('content="Summa hisobidagi mutlaq farq: 1-Davr - 2-Davr"',
     'content="Сумма ҳисобидаги мутлақ фарқ: 1-Давр - 2-Давр"'),
    ("content=\"Oldingi davrga nisbatan foiz hisobidagi o'sish (+) yoki pasayish (-) darajasi\"",
     'content="Олдинги даврга нисбатан фоиз ҳисобидаги ўсиш (+) ёки пасайиш (-) даражаси"'),
    
    # HTML template text strings
    # Monthly close view description
    ("Tanlangan oy bo'yicha tushum, xarajatlar, sof foyda va barcha amalga oshirilgan",
     "Танланган ой бўйича тушум, харажатлар, соф фойда ва барча амалга оширилган"),
    ("savdo bitimlari (cheklar) tahlili.", "савдо битимлари (чеклар) таҳлили."),
    
    # Buttons
    ("? 'Qayta Hisoblash & Yangilash'", "? 'Қайта Ҳисоблаш & Янгилаш'"),
    (": 'Ushbu Oyni Muhrlash & Saqlash'", ": 'Ушбу Ойни Муҳрлаш & Сақлаш'"),
    
    # Status messages
    ("oyi rasmiy yopilgan va arxivga muhrlangan.", "ойи расмий ёпилган ва архивга муҳрланган."),
    ("oyi ochiq (Hali yakuniy muhrlanmagan).", "ойи очиқ (Ҳали якуний муҳрланмаган)."),
    ("Muhrlangan sana:", "Муҳрланган сана:"),
    ("(Mas'ul:", "(Масъул:"),
    
    # KPI card subtitles
    (">JAMI TUSHUM (SAVDO)<", ">ЖАМИ ТУШУМ (САВДО)<"),
    (">MAHSULOT TANNARXI (COGS)<", ">МАҲСУЛОТ ТАННАРХИ (COGS)<"),
    (">ISH HAQI VA AVANSLAR<", ">ИШ ҲАҚИ ВА АВАНСLАР<"),
    (">HAQIQIY SOF FOYDA<", ">ҲАҚИҚИЙ СОФ ФОЙДА<"),
    (">SOF FOYDA<", ">СОФ ФОЙДА<"),
    
    # Stat footer text
    ("Tushumning ~", "Тушумнинг ~"),
    ("}}% qismi", "}}% қисми"),
    ("Doimiy: $", "Доимий: $"),
    (">+ Vyrabotka: $", ">+ Выработка: $"),
    (">Vyrabotka:<", ">Выработка:<"),
    (">Sof Foyda:<", ">Соф Фойда:<"),
    ("% Marja", "% Маржа"),
    
    # Evolution chart header text
    (">Har oy bo'yicha uzluksiz o'sish egri chizig'i<", ">Ҳар ой бўйича узлуксиз ўсиш эгри чизиғи<"),
    
    # Monthly Sales section buttons
    ("Tanlangan ({{ closeMonthInput }}) Oyi Savdolari", "Танланган ({{ closeMonthInput }}) Ойи Савдолари"),
    ("Arxivlangan Oylar Tarixi ({{ savedSnapshots.length }} ta oy)", "Архивланган Ойлар Тарихи ({{ savedSnapshots.length }} та ой)"),
    
    # Summary labels
    (">Jami Savdo:<", ">Жами Савдо:<"),
    (">To'langan:<", ">Тўланган:<"),
    (">Qarz:<", ">Қарз:<"),
    ("> Yangilash", "> Янгилаш"),
    
    # Table placeholder and search
    ('placeholder="Chek raqami, mijoz ismi yoki kassir..."', 'placeholder="Чек рақами, мижоз исми ёки кассир..."'),
    ("placeholder=\"To'lov usuli\"", 'placeholder="Тўлов усули"'),
    ("label=\"Barcha to'lov usullari\"", 'label="Барча тўлов усуллари"'),
    ('label="Naqd pul"', 'label="Нақд пул"'),
    ('label="Plastik karta"', 'label="Пластик карта"'),
    
    # Empty state texts
    (">Ushbu oy uchun savdo cheklari topilmadi<", ">Ушбу ой учун савдо чеклари топилмади<"),
    (">Qidiruv parametrlarini o'zgartiring yoki yangi sotuv amalga oshiring.<", ">Қидирув параметрларини ўзгартиринг ёки янги сотув амалга оширинг.<"),
    
    # Table column labels (hardcoded, not t() calls)
    ("label=\"Mijoz (Xaridor)\"", 'label="Мижоз (Харидор)"'),
    ("label=\"To'lov Usuli\"", 'label="Тўлов Усули"'),
    ('label="Mahsulotlar"', 'label="Маҳсулотлар"'),
    ("label=\"To'langan ($)\"", 'label="Тўланган ($)"'),
    ('label="Qarz ($)"', 'label="Қарз ($)"'),
    ('label="Vaqti"', 'label="Вақти"'),
    ('label="Bitimlar"', 'label="Битимлар"'),
    ('label="Rentabellik"', 'label="Рентабеллик"'),
    ('label="Muhrlangan sana"', 'label="Муҳрланган сана"'),
    ("label=\"Moliyaviy Ko'rsatkich\"", 'label="Молиявий Кўрсаткич"'),
    ('label="Mutlaq Farq (Delta)"', 'label="Мутлақ Фарқ (Делта)"'),
    ("label=\"O'sish Sur'ati (%)\"", 'label="Ўсиш Суръати (%)"'),
    ('label="Narxi ($)"', 'label="Нархи ($)"'),
    ('label="Jami ($)"', 'label="Жами ($)"'),
    
    # Payment tags
    ("\n                  Naqd\n", "\n                  Нақд\n"),
    ("\n                  Karta\n", "\n                  Карта\n"),
    ("\n                  Nasiya\n", "\n                  Насия\n"),
    ("\n                  O'tkazma\n", "\n                  Ўтказма\n"),
    ("|| 'Naqd'", "|| 'Нақд'"),
    
    # Products count
    ("}} xil", "}} хил"),
    # Deals count in archive
    ("}} ta savdo", "}} та савдо"),
    
    # Walk-in customer
    ("'Umumiy xaridor (Walk-in)'", "'Умумий харидор (Walk-in)'"),
    
    # Sale detail dialog
    (":title=\"`Savdo Cheki: ${selectedSaleDetail?.receipt_number || selectedSaleDetail?.id || ''}`\"",
     ':title="`Савдо Чеки: ${selectedSaleDetail?.receipt_number || selectedSaleDetail?.id || \'\'}`"'),
    (">Xaridor:<", ">Харидор:<"),
    (">Sana va Kassir:<", ">Сана ва Кассир:<"),
    (">JAMI CHEK SUMMASI:<", ">ЖАМИ ЧЕК СУММАСИ:<"),
    
    # Snapshot detail dialog
    ("Oyi Rasmiy Moliyaviy Arxiv Hisoboti`", "Ойи Расмий Молиявий Архив Ҳисоботи`"),
    (">Hisobot Davri:<", ">Ҳисобот Даври:<"),
    ("}} Oyi<", "}} Ойи<"),
    (">Sotuvlar soni:", ">Сотувлар сони:"),
    (">RASMIY MUHRLANGAN<", ">РАСМИЙ МУҲРЛАНГАН<"),
    ("> RASMIY MUHRLANGAN", "> РАСМИЙ МУҲРЛАНГАН"),
    (">Muhrlandi:", ">Муҳрланди:"),
    (">1. Jami Savdo & Tushum (Gross Revenue):<", ">1. Жами Савдо & Тушум (Gross Revenue):<"),
    (">2. Mahsulot Tannarxi (COGS):<", ">2. Маҳсулот Таннархи (COGS):<"),
    (">3. Doimiy Ishchilar Maoshi va Avanslar:<", ">3. Доимий Ишчилар Маоши ва Авансlар:<"),
    (">4. Qisqa Muddatli Ishchilar (Vyrabotka):<", ">4. Қисқа Муддатли Ишчилар (Выработка):<"),
    (">JAMI XARAJATLAR (TOTAL EXPENSES):<", ">ЖАМИ ХАРАЖАТЛАР (TOTAL EXPENSES):<"),
    (">HAQIQIY SOF FOYDA:<", ">ҲАҚИҚИЙ СОФ ФОЙДА:<"),
    ("* Ushbu ma'lumotlar arxivda muzlatilgan bo'lib, o'zgarishsiz saqlanadi.", "* Ушбу маълумотлар архивда музлатилган бўлиб, ўзгаришсиз сақланади."),
    
    # Archive empty state
    (">Hali yopilgan oylik moliyaviy hisobotlar mavjud emas<", ">Ҳали ёпилган ойлик молиявий ҳисоботлар мавжуд эмас<"),
    (">Yuqoridagi \"Ushbu Oyni Muhrlash & Saqlash\" tugmasi orqali o'tgan oylarni arxivga",
     '>Юқоридаги "Ушбу Ойни Муҳрлаш & Сақлаш" тугмаси орқали ўтган ойларни архивга'),
    ("saqlashingiz mumkin.<", "сақлашингиз мумкин.<"),
    
    # Muhrlangan tag
    ("> Muhrlangan", "> Муҳрланган"),
    ("> Ko'rish", "> Кўриш"),
    ("> Chekni ko'rish", "> Чекни кўриш"),
    
    # Compare view - radio buttons
    (">Oyma-oy (MoM)<", ">Ойма-ой (MoM)<"),
    (">Chorakma-chorak (QoQ)<", ">Чоракма-чорак (QoQ)<"),
    (">30 Kunlik<", ">30 Кунлик<"),
    (">Yillik (YoY)<", ">Йиллик (YoY)<"),
    (">Maxsus Sana<", ">Махсус Сана<"),
    (">Taqqoslash Turi:<", ">Таққослаш Тури:<"),
    
    # Compare KPI titles
    (">Jami Tushum O'sishi<", ">Жами Тушум Ўсиши<"),
    (">Tannarx Farqi (COGS)<", ">Таннарх Фарқи (COGS)<"),
    (">Ish Haqi Farqi (Payroll)<", ">Иш Ҳақи Фарқи (Payroll)<"),
    ("O'zgarishi<", "Ўзгариши<"),
    
    # Period labels in template
    (">1-Davr:<", ">1-Давр:<"),
    (">2-Davr:<", ">2-Давр:<"),
    (">1-Davr: <b>", ">1-Давр: <b>"),
    
    # Date pickers
    ('start-placeholder="Boshlanish"', 'start-placeholder="Бошланиш"'),
    ('end-placeholder="Tugash"', 'end-placeholder="Тугаш"'),
    
    # Chart header text
    ("Taqqoslash Grafikasi<", "Таққослаш Графикаси<"),
    (">1-Davr Daromad Strukturasi<", ">1-Давр Даромад Структураси<"),
    (">Ko'rsatkichlarning To'liq Delta va Foiz O'zgarishi Jadvali<",
     ">Кўрсаткичларнинг Тўлиқ Делта ва Фоиз Ўзгариши Жадвали<"),
    
    # Avanslar label fix
    ("Avanslar ($)\"", 'Авансlар ($)"'),
]

count = 0
for old, new in REPLACEMENTS:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  ✓ [{count}] Replaced: {old[:70]}...")
    else:
        # Try to find similar content for debugging
        pass

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total replacements applied: {count}")
