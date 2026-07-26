import re

with open('journal/forms.py', 'r', encoding='utf-8') as f:
    content = f.read()

patterns = [
    r"(label)=(['\"][^'\"]+['\"])",
    r"('placeholder'): (['\"][^'\"]+['\"])",
    r"(help_text)=(['\"][^'\"]+['\"])",
    r"(forms\.ValidationError)\((['\"][^'\"]+['\"])\)"
]

for pat in patterns:
    def repl(m):
        prefix = m.group(1)
        string_val = m.group(2)
        if prefix == "'placeholder'":
            return f"'placeholder': _({string_val})"
        elif prefix == "forms.ValidationError":
            return f"forms.ValidationError(_({string_val}))"
        else:
            return f"{prefix}=_({string_val})"
    content = re.sub(pat, repl, content)

with open('journal/forms.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced strings in journal/forms.py')
