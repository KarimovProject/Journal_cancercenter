import ast

new_translations = [
    '0000-0000-0000-0000',
    '10.1234/oncoscience.2025.01.005',
    'Affiliation (en)',
    'Annotatsiya (en)',
    'Annotatsiya (ru)',
    'Annotatsiya (uz)',
    'Bu email allaqachon roʻyxatdan oʻtgan.',
    'Bu foydalanuvchi nomi band.',
    'DOI yoki havola (ixtiyoriy)',
    'Email *',
    'F.I.O. *',
    'F.I.O.',
    'Faqat tahririyat uchun maxfiy izohlar...',
    'Fayl nomi',
    'Foydalanuvchi nomi *',
    'Har bir muallif F.I.O.sini yangi qatorda yozing. Siz avtomatik birinchi muallif bo\u02bblasiz.',
    'Har bir muallifni yangi qatorda yozing:\\nAliyev Vali\\nKarimova Saoda',
    'Ilmiy daraja',
    'Ish joyi (ru)',
    'Ish joyi (uz)',
    'Ish joyi / Afiliatsiya *',
    'Jurnal soni (ixtiyoriy)',
    'Kalit so\u02bblar (vergul bilan ajrating)',
    'Masalan: Vol. 5, No. 2, 2025',
    'Masalan: t.f.d.',
    'Mavjud sondan tanlang yoki o\u02bbzingiz yozing. Format: Vol. X, No. Y, YYYY',
    'Muallif(lar), sarlavha, jurnal, yil, sahifalar.',
    'Muallifga yoziladigan izohlar (qanday kamchiliklar bor, nimalarni to\u02bbg\u02bbrilash kerak)...',
    'Mualliflar manfaatlar to\u02bbqnashuvi yo\u02bbqligini bildiradilar.',
    'ORCID iD',
    'Oʻzbek tilidagi sarlavha majburiy.',
    'PDF fayl yuklash majburiy.',
    'Parol (qayta) *',
    'Parol *',
    'Parollar mos kelmadi.',
    'Qo\u02bbshimcha mualliflar (ixtiyoriy)',
    'Sarlavha (en)',
    'Sarlavha (ru)',
    'Sarlavha (uz)',
    'Tadqiqot etika komissiyasi tomonidan tasdiqlangan.',
    'Tagyozuv (ixtiyoriy)',
    'Ushbu tadqiqot ... tomonidan moliyalashtirilgan.',
    'email@example.com',
    'saraton, immunoterapiya, kimyoterapiya...',
    't.f.n., t.f.d., dotsent...',
]

RU_NEW = {
    '0000-0000-0000-0000': '0000-0000-0000-0000',
    '10.1234/oncoscience.2025.01.005': '10.1234/oncoscience.2025.01.005',
    'Affiliation (en)': 'Аффилиация (англ)',
    'Annotatsiya (en)': 'Аннотация (англ)',
    'Annotatsiya (ru)': 'Аннотация (рус)',
    'Annotatsiya (uz)': 'Аннотация (узб)',
    'Bu email allaqachon roʻyxatdan oʻtgan.': 'Этот email уже зарегистрирован.',
    'Bu foydalanuvchi nomi band.': 'Это имя пользователя занято.',
    'DOI yoki havola (ixtiyoriy)': 'DOI или ссылка (необязательно)',
    'Email *': 'Email *',
    'F.I.O. *': 'Ф.И.О. *',
    'F.I.O.': 'Ф.И.О.',
    'Faqat tahririyat uchun maxfiy izohlar...': 'Секретные комментарии только для редакции...',
    'Fayl nomi': 'Имя файла',
    'Foydalanuvchi nomi *': 'Имя пользователя *',
    'Har bir muallif F.I.O.sini yangi qatorda yozing. Siz avtomatik birinchi muallif bo\u02bblasiz.': 'Напишите Ф.И.О. каждого автора с новой строки. Вы автоматически станете первым автором.',
    'Har bir muallifni yangi qatorda yozing:\nAliyev Vali\nKarimova Saoda': 'Пишите каждого автора с новой строки:\nАлиев Вали\nКаримова Саодат',
    'Ilmiy daraja': 'Ученая степень',
    'Ish joyi (ru)': 'Место работы (рус)',
    'Ish joyi (uz)': 'Место работы (узб)',
    'Ish joyi / Afiliatsiya *': 'Место работы / Аффилиация *',
    'Jurnal soni (ixtiyoriy)': 'Выпуск журнала (необязательно)',
    'Kalit so\u02bblar (vergul bilan ajrating)': 'Ключевые слова (через запятую)',
    'Masalan: Vol. 5, No. 2, 2025': 'Например: Vol. 5, No. 2, 2025',
    'Masalan: t.f.d.': 'Например: д.м.н.',
    'Mavjud sondan tanlang yoki o\u02bbzingiz yozing. Format: Vol. X, No. Y, YYYY': 'Выберите из существующего выпуска или напишите свой. Формат: Vol. X, No. Y, YYYY',
    'Muallif(lar), sarlavha, jurnal, yil, sahifalar.': 'Автор(ы), заголовок, журнал, год, страницы.',
    'Muallifga yoziladigan izohlar (qanday kamchiliklar bor, nimalarni to\u02bbg\u02bbrilash kerak)...': 'Комментарии автору (какие есть недостатки, что нужно исправить)...',
    'Mualliflar manfaatlar to\u02bbqnashuvi yo\u02bbqligini bildiradilar.': 'Авторы заявляют об отсутствии конфликта интересов.',
    'ORCID iD': 'ORCID iD',
    'Oʻzbek tilidagi sarlavha majburiy.': 'Заголовок на узбекском обязателен.',
    'PDF fayl yuklash majburiy.': 'Загрузка PDF файла обязательна.',
    'Parol (qayta) *': 'Пароль (повторно) *',
    'Parol *': 'Пароль *',
    'Parollar mos kelmadi.': 'Пароли не совпадают.',
    'Qo\u02bbshimcha mualliflar (ixtiyoriy)': 'Соавторы (необязательно)',
    'Sarlavha (en)': 'Заголовок (англ)',
    'Sarlavha (ru)': 'Заголовок (рус)',
    'Sarlavha (uz)': 'Заголовок (узб)',
    'Tadqiqot etika komissiyasi tomonidan tasdiqlangan.': 'Исследование одобрено этическим комитетом.',
    'Tagyozuv (ixtiyoriy)': 'Подпись (необязательно)',
    'Ushbu tadqiqot ... tomonidan moliyalashtirilgan.': 'Данное исследование профинансировано...',
    'email@example.com': 'email@example.com',
    'saraton, immunoterapiya, kimyoterapiya...': 'рак, иммунотерапия, химиотерапия...',
    't.f.n., t.f.d., dotsent...': 'к.м.н., д.м.н., доцент...',
}

EN_NEW = {
    '0000-0000-0000-0000': '0000-0000-0000-0000',
    '10.1234/oncoscience.2025.01.005': '10.1234/oncoscience.2025.01.005',
    'Affiliation (en)': 'Affiliation (en)',
    'Annotatsiya (en)': 'Abstract (en)',
    'Annotatsiya (ru)': 'Abstract (ru)',
    'Annotatsiya (uz)': 'Abstract (uz)',
    'Bu email allaqachon roʻyxatdan oʻtgan.': 'This email is already registered.',
    'Bu foydalanuvchi nomi band.': 'This username is taken.',
    'DOI yoki havola (ixtiyoriy)': 'DOI or link (optional)',
    'Email *': 'Email *',
    'F.I.O. *': 'Full Name *',
    'F.I.O.': 'Full Name',
    'Faqat tahririyat uchun maxfiy izohlar...': 'Secret comments for editorial board only...',
    'Fayl nomi': 'File name',
    'Foydalanuvchi nomi *': 'Username *',
    'Har bir muallif F.I.O.sini yangi qatorda yozing. Siz avtomatik birinchi muallif bo\u02bblasiz.': 'Write each author\'s full name on a new line. You will automatically be the first author.',
    'Har bir muallifni yangi qatorda yozing:\nAliyev Vali\nKarimova Saoda': 'Write each author on a new line:\nAliyev Vali\nKarimova Saoda',
    'Ilmiy daraja': 'Academic degree',
    'Ish joyi (ru)': 'Affiliation (ru)',
    'Ish joyi (uz)': 'Affiliation (uz)',
    'Ish joyi / Afiliatsiya *': 'Affiliation *',
    'Jurnal soni (ixtiyoriy)': 'Journal issue (optional)',
    'Kalit so\u02bblar (vergul bilan ajrating)': 'Keywords (comma separated)',
    'Masalan: Vol. 5, No. 2, 2025': 'E.g.: Vol. 5, No. 2, 2025',
    'Masalan: t.f.d.': 'E.g.: Ph.D.',
    'Mavjud sondan tanlang yoki o\u02bbzingiz yozing. Format: Vol. X, No. Y, YYYY': 'Choose from an existing issue or write your own. Format: Vol. X, No. Y, YYYY',
    'Muallif(lar), sarlavha, jurnal, yil, sahifalar.': 'Author(s), title, journal, year, pages.',
    'Muallifga yoziladigan izohlar (qanday kamchiliklar bor, nimalarni to\u02bbg\u02bbrilash kerak)...': 'Comments for the author (what flaws exist, what to fix)...',
    'Mualliflar manfaatlar to\u02bbqnashuvi yo\u02bbqligini bildiradilar.': 'The authors declare no conflict of interest.',
    'ORCID iD': 'ORCID iD',
    'Oʻzbek tilidagi sarlavha majburiy.': 'Uzbek title is mandatory.',
    'PDF fayl yuklash majburiy.': 'PDF file upload is mandatory.',
    'Parol (qayta) *': 'Password (confirm) *',
    'Parol *': 'Password *',
    'Parollar mos kelmadi.': 'Passwords do not match.',
    'Qo\u02bbshimcha mualliflar (ixtiyoriy)': 'Co-authors (optional)',
    'Sarlavha (en)': 'Title (en)',
    'Sarlavha (ru)': 'Title (ru)',
    'Sarlavha (uz)': 'Title (uz)',
    'Tadqiqot etika komissiyasi tomonidan tasdiqlangan.': 'The study was approved by the ethics committee.',
    'Tagyozuv (ixtiyoriy)': 'Caption (optional)',
    'Ushbu tadqiqot ... tomonidan moliyalashtirilgan.': 'This study was funded by...',
    'email@example.com': 'email@example.com',
    'saraton, immunoterapiya, kimyoterapiya...': 'cancer, immunotherapy, chemotherapy...',
    't.f.n., t.f.d., dotsent...': 'Ph.D., MD, Associate Professor...',
}

with open('compile_translations.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Insert RU_NEW into RU
ru_match = re.search(r'RU\s*=\s*\{', content)
if ru_match:
    idx = ru_match.end()
    ru_str = ''
    for k, v in RU_NEW.items():
        ru_str += f"    {repr(k)}: {repr(v)},\n"
    content = content[:idx] + '\n' + ru_str + content[idx:]

# Insert EN_NEW into EN
en_match = re.search(r'EN\s*=\s*\{', content)
if en_match:
    idx = en_match.end()
    en_str = ''
    for k, v in EN_NEW.items():
        en_str += f"    {repr(k)}: {repr(v)},\n"
    content = content[:idx] + '\n' + en_str + content[idx:]

with open('compile_translations.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated compile_translations.py")
