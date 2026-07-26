import re
with open('journal/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r"_\((['\"][^'\"]+['\"])\)", content)
with open('compile_translations.py', 'r', encoding='utf-8') as f:
    compile_content = f.read()

missing = []
for m in sorted(set(matches)):
    if m not in compile_content:
        missing.append(m)

with open('missing_translations.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(missing))
