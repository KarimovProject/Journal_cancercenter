import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oncoscience.settings')
django.setup()
from journal.models import Author, Article
from django.utils.text import slugify

for a in Author.objects.all():
    new_slug = slugify(a.full_name)
    if not new_slug or not new_slug.replace('-', '').isalnum():
        new_slug = 'author-' + str(a.id)
    a.slug = new_slug
    a.save()

for a in Article.objects.all():
    new_slug = slugify(a.title_uz)
    if not new_slug or not new_slug.replace('-', '').isalnum():
        new_slug = 'article-' + str(a.id)
    a.slug = new_slug
    a.save()
print('Slugs fixed successfully')
