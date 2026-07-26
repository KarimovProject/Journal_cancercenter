from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Issue

class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Article.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class IssueSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Issue.objects.all()

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['journal:home', 'journal:article_list', 'journal:issue_list']

    def location(self, item):
        return reverse(item)

sitemaps = {
    'articles': ArticleSitemap,
    'issues': IssueSitemap,
    'static': StaticViewSitemap,
}
