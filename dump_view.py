with open('journal/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('submit_view.txt', 'w', encoding='utf-8') as out:
    start = 0
    for i, line in enumerate(lines):
        if 'def submit_article' in line:
            start = i
            break
    for i in range(start, start + 60):
        if i < len(lines):
            out.write(lines[i])
