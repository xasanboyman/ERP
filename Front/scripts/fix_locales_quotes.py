import json
import re

uz_p = '/home/xasanboy/ERP/Front/src/locales/uz.ts'
en_p = '/home/xasanboy/ERP/Front/src/locales/en.ts'

with open(uz_p, 'r', encoding='utf-8') as f:
    uz_t = f.read()

uz_t = uz_t.replace("newPasswordOptional: 'Yangi parol (o'zgartirish shart bo'lmasa bo'sh qoldiring)',", "newPasswordOptional: \"Yangi parol (o'zgartirish shart bo'lmasa bo'sh qoldiring)\",")
uz_t = uz_t.replace("adminPasswordVerifyPlaceholder: 'O'zgartirishni tasdiqlash uchun admin parolingizni kiriting',", "adminPasswordVerifyPlaceholder: \"O'zgartirishni tasdiqlash uchun admin parolingizni kiriting\",")
uz_t = uz_t.replace("workerExtraInfo: 'Xodim haqida qo'shimcha ma'lumotlar',", "workerExtraInfo: \"Xodim haqida qo'shimcha ma'lumotlar\",")

with open(uz_p, 'w', encoding='utf-8') as f:
    f.write(uz_t)

from generate_cr_locale import convert_uz_to_cr
convert_uz_to_cr()
print("Fixed uz.ts and cr.ts quotes!")
