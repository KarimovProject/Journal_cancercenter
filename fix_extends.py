import io

file_path = 'templates/journal/submit_article.html'
with io.open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('{% extends "base.html" %}', '{% extends "journal/dashboard/base_dashboard.html" %}')

with io.open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
