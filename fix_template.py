import os

file_path = 'templates/journal/submit_article.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Change extends
html = html.replace("{% extends 'journal/base.html' %}", "{% extends 'journal/dashboard/base_dashboard.html' %}")
html = html.replace('{% block content %}', '{% block dashboard_content %}')

# Update container styles
html = html.replace('<div class="container form-container">', '<div class="max-w-4xl mx-auto py-8">')
html = html.replace('<h1 class="form-title">{% trans "Yangi maqola yuborish" %}</h1>', '<div class="mb-8 pb-4 border-b border-gray-200 dark:border-slate-700"><h1 class="text-3xl font-bold text-slate-800 dark:text-white font-display mb-2">{% trans "Yangi maqola yuborish" %}</h1><p class="text-slate-500 dark:text-slate-400">{% trans "Iltimos, maqolangiz haqidagi ma\'lumotlarni to\'ldiring va kerakli fayllarni yuklang." %}</p></div><div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 p-8">')

# Add the closing div before the endblock
html = html.replace('</div>\n</div>\n\n{{ form.media }}', '</div>\n</div>\n</div>\n\n{{ form.media }}')

# Update form styles
html = html.replace('class="submit-form"', 'class="submit-form space-y-8"')
html = html.replace('class="form-section-title"', 'class="text-xl font-bold text-slate-800 dark:text-white mb-4 mt-8 pb-2 border-b border-gray-100 dark:border-slate-700"')
html = html.replace('class="form-group"', 'class="space-y-2 mb-4"')
html = html.replace('class="form-label"', 'class="block text-sm font-semibold text-slate-700 dark:text-slate-300"')
html = html.replace('class="form-input"', 'class="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-colors"')
html = html.replace('class="form-help"', 'class="text-xs text-slate-500 dark:text-slate-400 mt-1"')

# Update buttons
html = html.replace('class="btn btn-outline btn-add-row"', 'class="btn-add-row inline-flex items-center px-4 py-2 text-sm font-medium text-teal-600 dark:text-teal-400 bg-teal-50 dark:bg-teal-900/30 border border-teal-200 dark:border-teal-800 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/50 transition-colors"')
html = html.replace('class="btn btn-block"', 'class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 transition-all"')

# Formset rows and grids
html = html.replace('class="formset-row"', 'class="formset-row p-4 mb-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 relative"')
html = html.replace('class="formset-grid"', 'class="formset-grid grid grid-cols-1 md:grid-cols-12 gap-4 items-end"')
html = html.replace('class="formset-cell formset-order"', 'class="formset-cell formset-order md:col-span-2"')
html = html.replace('class="formset-cell formset-grow"', 'class="formset-cell formset-grow md:col-span-5"')
html = html.replace('class="formset-del"', 'class="formset-del text-red-500 hover:text-red-700 text-sm mt-2 cursor-pointer flex items-center"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
