from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Article


class LatestArticlesFeed(Feed):
    """RSS feed of the most recently published articles."""

    title = 'Oncoscience — so\'nggi maqolalar'
    description = _('Onkologiya va radiologiya sohasidagi so\'nggi ilmiy maqolalar.')

    def link(self):
        return reverse('journal:article_list')

    def items(self):
        return (
            Article.objects.filter(status=Article.Status.PUBLISHED)
            .prefetch_related('authors')
            .order_by('-publication_date', '-created_at')[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.abstract or item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        from datetime import datetime, time
        if item.publication_date:
            return datetime.combine(item.publication_date, time.min)
        return item.created_at

    def item_author_name(self, item):
        return ', '.join(a.full_name for a in item.authors.all())
