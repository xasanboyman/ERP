import re

an_p = '/home/xasanboy/ERP/Front/src/views/Dashboard/Analysis.vue'

with open(an_p, 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('<template>')
script_part = parts[0]
template_part = '<template>' + parts[1]

lines = script_part.splitlines()
fixed_lines = []
for line in lines:
    if "{{ t(" in line or "{{t(" in line:
        # replace standalone '{{ t('key') }}' -> t('key')
        line = re.sub(r"""['"]\{\{\s*t\(['"](.*?)['"]\)\s*\}\}['"]""", r"t('\1')", line)
        # replace embedded '... {{ t('key') }} ...' -> `... ${t('key')} ...`
        line = re.sub(r"""'([^'\n]*)\{\{\s*t\(['"](.*?)['"]\)\s*\}\}([^'\n]*)'""", r"`\1${t('\2')}\3`", line)
        line = re.sub(r'''"([^"\n]*)\{\{\s*t\(['"](.*?)['"]\)\s*\}\}([^"\n]*)"''', r"`\1${t('\2')}\3`", line)
    fixed_lines.append(line)

script_part = '\n'.join(fixed_lines)
new_content = script_part + template_part

with open(an_p, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed script part in Analysis.vue!")
