import traceback
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oncoscience.settings')
django.setup()
from journal.models import Article
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from journal.views import article_detail

article = Article.objects.order_by('-created_at').first()
print(f'Testing article: {article.title_uz}')
factory = RequestFactory()
request = factory.get(f'/ilm-fan/maqolalar/{article.slug}/')
request.session = {}
request.user = AnonymousUser()

try:
    response = article_detail(request, article.slug)
    print('SUCCESS, response status:', response.status_code)
    if response.status_code != 200:
        print(response.content.decode('utf-8'))
except Exception as e:
    print('ERROR OCCURRED:')
    traceback.print_exc()
