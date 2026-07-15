from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article, Author, Conference, JournalUpdate


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return [
            'journal:home',
            'journal:article_list',
            'journal:issue_list',
            'journal:editorial_board',
            'journal:conference_list',
            'journal:for_authors',
        ]

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Article.objects.filter(status=Article.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class AuthorSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return Author.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class ConferenceSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return Conference.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class UpdateSitemap(Sitemap):
    priority = 0.4
    changefreq = 'weekly'

    def items(self):
        return JournalUpdate.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_date

    def location(self, obj):
        return obj.get_absolute_url()


sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'authors': AuthorSitemap,
    'conferences': ConferenceSitemap,
    'updates': UpdateSitemap,
}
