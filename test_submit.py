import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oncoscience.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from journal.models import Category

user, _ = User.objects.get_or_create(username='testuser', email='test@example.com')
user.set_password('password')
user.save()

cat, _ = Category.objects.get_or_create(name_uz='Test', slug='test')

c = Client(HTTP_HOST='journal.abdullatif.uz')
c.force_login(user)

with open('test.pdf', 'wb') as f:
    f.write(b'%PDF-1.4 dummy pdf content')

with open('test.pdf', 'rb') as pdf:
    data = {
        'title_uz': 'Test title',
        'abstract_uz': 'Test abstract',
        'article_type': 'original_article',
        'category': cat.id,
        'pdf_file': pdf,
        
        # Formsets
        'ref-TOTAL_FORMS': '0',
        'ref-INITIAL_FORMS': '0',
        'ref-MIN_NUM_FORMS': '0',
        'ref-MAX_NUM_FORMS': '1000',

        'fig-TOTAL_FORMS': '0',
        'fig-INITIAL_FORMS': '0',
        'fig-MIN_NUM_FORMS': '0',
        'fig-MAX_NUM_FORMS': '1000',

        'supp-TOTAL_FORMS': '0',
        'supp-INITIAL_FORMS': '0',
        'supp-MIN_NUM_FORMS': '0',
        'supp-MAX_NUM_FORMS': '1000',
    }
    
    print('Submitting...')
    resp = c.post('/ilm-fan/maqola-yuborish/', data)
    print('Response status:', resp.status_code)
    if resp.status_code != 302:
        print('Form errors:', resp.context['form'].errors if hasattr(resp, 'context') and resp.context and 'form' in resp.context else 'No form context')
