import os

for root, dirs, files in os.walk('/home/xasanboy/ERP/Front/src/views'):
    for f in files:
        if f.endswith('.vue'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fp:
                c = fp.read()
            if r"\'" in c:
                c = c.replace(r"\'", "'")
                with open(p, 'w', encoding='utf-8') as fp:
                    fp.write(c)
                print(f"Cleaned: {f}")
