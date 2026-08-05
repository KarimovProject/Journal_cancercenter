import os
import polib

locales = ['en', 'ru']
base_path = r'd:\Projects\Journal_cancercenter\locale'

for lang in locales:
    po_path = os.path.join(base_path, lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(base_path, lang, 'LC_MESSAGES', 'django.mo')
    
    if os.path.exists(po_path):
        # 1. Fix the multiline syntax error first manually
        with open(po_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        bad_id = 'msgid "Har bir muallifni yangi qatorda yozing:\nAliyev Vali\nKarimova Saoda"'
        good_id = 'msgid ""\n"Har bir muallifni yangi qatorda yozing:\\n"\n"Aliyev Vali\\n"\n"Karimova Saoda"'
        content = content.replace(bad_id, good_id)
        
        bad_str = 'msgstr "Write each author on a new line:\nAliyev Vali\nKarimova Saoda"'
        good_str = 'msgstr ""\n"Write each author on a new line:\\n"\n"Aliyev Vali\\n"\n"Karimova Saoda"'
        content = content.replace(bad_str, good_str)
        
        bad_str_ru = 'msgstr "Пишите каждого автора с новой строки:\nАлиев Вали\nКаримова Саодат"'
        good_str_ru = 'msgstr ""\n"Пишите каждого автора с новой строки:\\n"\n"Алиев Вали\\n"\n"Каримова Саодат"'
        content = content.replace(bad_str_ru, good_str_ru)
        
        with open(po_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # 2. Open with polib to do the string replacement
        try:
            po = polib.pofile(po_path)
        except Exception as e:
            print(f"Failed to parse {po_path}: {e}")
            continue

        modified = False
        
        for entry in po:
            if 'Oncoscience' in entry.msgid:
                entry.msgid = entry.msgid.replace('Oncoscience', 'Central Asian Cancer Sciences')
                modified = True
            
            if 'Oncoscience' in entry.msgstr:
                entry.msgstr = entry.msgstr.replace('Oncoscience', 'Central Asian Cancer Sciences')
                modified = True
                
        if modified:
            po.save(po_path)
            print(f"Updated translations in {po_path}")
        
        # 3. Compile regardless, to ensure .mo is up to date
        po.save_as_mofile(mo_path)
        print(f"Compiled {mo_path}")
    else:
        print(f"Not found: {po_path}")
