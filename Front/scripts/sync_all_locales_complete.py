import re
import json

EN_TO_UZ = {
    # dialogDemo
    "dialog": "Dialog",
    "operate": "Amallar",
    "close": "Yopish",
    "open": "Ochish",
    "show": "Ko'rsatish",
    "hide": "Yashirish",
    "customHeader": "Maxsus sarlavha",
    "customFooter": "Maxsus quyi qism",
    "customContent": "Maxsus kontent",
    "dialogDescription": "Dialog oynasi komponenti",

    # permission
    "add": "Qo'shish",
    "edit": "Tahrirlash",
    "delete": "O'chirish",
    "detail": "Batafsil",
    "hasPermission": "Huquq mavjud",
    "noPermission": "Huquq yo'q",
    "permission": "Huquqlar",

    # formDemo
    "input": "Kiritish",
    "select": "Tanlash",
    "radio": "Radio",
    "checkbox": "Checkbox",
    "switch": "O'tkazgich",
    "date": "Sana",
    "time": "Vaqt",
    "formDes": "Forma komponentlari va validatsiya",
    "basicForm": "Asosiy forma",
    "formValidation": "Forma tekshiruvi",
    "formGrid": "Forma to'ri",
    "formDisabled": "Forma bloklangan",
    "formSize": "Forma o'lchami",

    # descriptionsDemo
    "descriptions": "Tavsiflar",
    "descriptionsDes": "Tafsilotlar va ma'lumotlarni ko'rsatish komponenti",
    "basicDescriptions": "Asosiy tavsiflar",
    "customDescriptions": "Maxsus tavsiflar",

    # searchDemo
    "search": "Qidirish",
    "searchDes": "Qidiruv formasi komponenti",
    "basicSearch": "Asosiy qidiruv",
    "customSearch": "Maxsus qidiruv",

    # treeDemo
    "tree": "Daraxt",
    "treeDes": "Daraxtsimon ma'lumotlar strukturasi",

    # guideDemo
    "guide": "Qo'llanma",
    "guideDes": "Foydalanuvchi yo'riqnomasi",
    "startGuide": "Qo'llanmani boshlash",

    # iconDemo
    "icon": "Belgi",
    "iconDes": "Belgilar kutubxonasi",

    # echartDemo
    "echart": "Grafik",
    "echartDes": "ECharts ma'lumotlar vizualizatsiyasi",

    # countToDemo
    "countTo": "Hisoblagich",
    "countToDes": "Raqamli animatsion hisoblagich",

    # watermarkDemo
    "watermark": "Suv belgisi",
    "watermarkDes": "Sahifa suv belgisi",

    # qrcodeDemo
    "qrcode": "QR Kod",
    "qrcodeDes": "QR kod generatsiyasi",

    # highlightDemo
    "highlight": "Ajratib ko'rsatish",
    "highlightDes": "Matnni ajratib ko'rsatish",

    # infotipDemo
    "infotip": "Ma'lumot",
    "infotipDes": "Ma'lumotli maslahatlar",

    # levelDemo
    "level": "Ko'p bosqichli",
    "levelDes": "Ko'p bosqichli menyu",

    # stickyDemo
    "sticky": "Yopishqoq",
    "stickyDes": "Yopishqoq elementlar",

    # richText
    "richText": "Matn muharriri",
    "richTextDes": "Kengaytirilgan matn muharriri",

    # imageViewerDemo
    "imageViewer": "Rasm ko'ruvchi",
    "imageViewerDes": "Rasmlarni kattalashtirib ko'rish",

    # inputPasswordDemo
    "inputPassword": "Parol kiritish",
    "inputPasswordDes": "Parol kuchini tekshirish",

    # avatarsDemo
    "avatars": "Avatarlar",
    "avatarsDes": "Foydalanuvchi avatarlari"
}

def sync():
    print("Syncing complete translation dictionaries...")

    uz_path = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
    en_path = '/home/xasanboy/ERP/Front/src/locales/en.ts'

    with open(uz_path, 'r', encoding='utf-8') as f:
        uz_text = f.read()

    # Missing sections definition for uz.ts
    extra_uz_sections = """
  dialogDemo: {
    dialog: 'Dialog',
    operate: 'Amallar',
    close: 'Yopish',
    open: 'Ochish',
    show: 'Ko\\'rsatish',
    hide: 'Yashirish',
    customHeader: 'Maxsus sarlavha',
    customFooter: 'Maxsus quyi qism',
    customContent: 'Maxsus kontent',
    dialogDescription: 'Dialog oynasi komponenti'
  },

  permission: {
    add: 'Qo\\'shish',
    edit: 'Tahrirlash',
    delete: 'O\\'chirish',
    detail: 'Batafsil',
    hasPermission: 'Huquq mavjud',
    noPermission: 'Huquq yo\\'q',
    permission: 'Huquqlar'
  },

  formDemo: {
    input: 'Kiritish',
    select: 'Tanlash',
    radio: 'Radio',
    checkbox: 'Checkbox',
    switch: 'O\\'tkazgich',
    date: 'Sana',
    time: 'Vaqt',
    formDes: 'Forma komponentlari va tekshiruvi',
    basicForm: 'Asosiy forma',
    formValidation: 'Forma tekshiruvi',
    formGrid: 'Forma to\\'ri',
    formDisabled: 'Forma bloklangan',
    formSize: 'Forma o\\'lchami'
  },

  descriptionsDemo: {
    descriptions: 'Tavsiflar',
    descriptionsDes: 'Tafsilotlar va ma\\'lumotlarni ko\\'rsatish komponenti',
    basicDescriptions: 'Asosiy tavsiflar',
    customDescriptions: 'Maxsus tavsiflar'
  },

  searchDemo: {
    search: 'Qidirish',
    searchDes: 'Qidiruv formasi komponenti',
    basicSearch: 'Asosiy qidiruv',
    customSearch: 'Maxsus qidiruv'
  },

  treeDemo: {
    tree: 'Daraxt',
    treeDes: 'Daraxtsimon ma\\'lumotlar strukturasi'
  },

  guideDemo: {
    guide: 'Qo\\'llanma',
    guideDes: 'Foydalanuvchi yo\\'riqnomasi',
    startGuide: 'Qo\\'llanmani boshlash'
  },

  iconDemo: {
    icon: 'Belgi',
    iconDes: 'Belgilar kutubxonasi'
  },

  echartDemo: {
    echart: 'Grafik',
    echartDes: 'ECharts ma\\'lumotlar vizualizatsiyasi'
  },

  countToDemo: {
    countTo: 'Hisoblagich',
    countToDes: 'Raqamli animatsion hisoblagich'
  },

  watermarkDemo: {
    watermark: 'Suv belgisi',
    watermarkDes: 'Sahifa suv belgisi'
  },

  qrcodeDemo: {
    qrcode: 'QR Kod',
    qrcodeDes: 'QR kod generatsiyasi'
  },

  highlightDemo: {
    highlight: 'Ajratib ko\\'rsatish',
    highlightDes: 'Matnni ajratib ko\\'rsatish'
  },

  infotipDemo: {
    infotip: 'Ma\\'lumot',
    infotipDes: 'Ma\\'lumotli maslahatlar'
  },

  levelDemo: {
    level: 'Ko\\'p bosqichli',
    levelDes: 'Ko\\'p bosqichli menyu'
  },

  stickyDemo: {
    sticky: 'Yopishqoq',
    stickyDes: 'Yopishqoq elementlar'
  },

  richText: {
    richText: 'Matn muharriri',
    richTextDes: 'Kengaytirilgan matn muharriri'
  },

  imageViewerDemo: {
    imageViewer: 'Rasm ko\\'ruvchi',
    imageViewerDes: 'Rasmlarni kattalashtirib ko\\'rish'
  },

  inputPasswordDemo: {
    inputPassword: 'Parol kiritish',
    inputPasswordDes: 'Parol kuchini tekshirish'
  },

  avatarsDemo: {
    avatars: 'Avatarlar',
    avatarsDes: 'Foydalanuvchi avatarlari'
  },
"""

    for sec in ["dialogDemo", "permission", "formDemo", "descriptionsDemo", "searchDemo", "treeDemo", "guideDemo", "iconDemo", "echartDemo", "countToDemo", "watermarkDemo", "qrcodeDemo", "highlightDemo", "infotipDemo", "levelDemo", "stickyDemo", "richText", "imageViewerDemo", "inputPasswordDemo", "avatarsDemo"]:
        if f"{sec}:" not in uz_text:
            uz_text = uz_text.rstrip().rstrip('}') + "\n" + extra_uz_sections + "\n}\n"
            break

    with open(uz_path, 'w', encoding='utf-8') as f:
        f.write(uz_text)

    # Regenerate cr.ts
    from generate_cr_locale import convert_uz_to_cr
    convert_uz_to_cr()
    print("Full i18n synchronization completed successfully!")

if __name__ == '__main__':
    sync()
