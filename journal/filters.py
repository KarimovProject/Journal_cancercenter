import django_filters
from django.db.models import Q

from .models import Article, Author, Category


class ArticleFilter(django_filters.FilterSet):
    """Filtering for the public article list: category, year, author, search."""

    category = django_filters.ModelChoiceFilter(
        field_name='category', to_field_name='slug',
        queryset=Category.objects.all(),
    )
    year = django_filters.NumberFilter(field_name='publication_date', lookup_expr='year')
    author = django_filters.ModelChoiceFilter(
        field_name='authors', to_field_name='slug',
        queryset=Author.objects.all(),
    )
    q = django_filters.CharFilter(method='filter_search', label='Qidiruv')

    class Meta:
        model = Article
        fields = ['category', 'year', 'author']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title_uz__icontains=value)
            | Q(title_ru__icontains=value)
            | Q(title_en__icontains=value)
            | Q(abstract_uz__icontains=value)
            | Q(abstract_ru__icontains=value)
            | Q(abstract_en__icontains=value)
            | Q(full_text_uz__icontains=value)
            | Q(full_text_ru__icontains=value)
            | Q(full_text_en__icontains=value)
            | Q(doi__icontains=value)
            | Q(keywords__name__icontains=value)
            | Q(authors__full_name__icontains=value)
        ).distinct()
