import re

with open('journal/forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r"_\((['\"][^'\"]+['\"])\)", content)
with open('extracted_strings.txt', 'w', encoding='utf-8') as out:
    for m in sorted(set(matches)):
        out.write(m + '\n')
