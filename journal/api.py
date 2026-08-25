from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.pagination import SmallResultsPagination
from .filters import ArticleFilter
from .models import Article, Author, Category, Conference
from .serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    AuthorSerializer,
    CategorySerializer,
    ConferenceSerializer,
)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only API for published articles.

    Consumed by the main cancercenter.uz site (e.g. "latest articles" block).
    Pagination: StandardResultsPagination (12/page) — base.py dan olinadi.
    """

    permission_classes = [AllowAny]
    serializer_class = ArticleListSerializer
    filterset_class = ArticleFilter
    lookup_field = 'slug'
    search_fields = ['title_uz', 'title_ru', 'title_en', 'abstract_uz']
    ordering_fields = ['publication_date', 'views_count', 'citation_count']
    ordering = ['-publication_date']

    def get_queryset(self):
        return (
            Article.objects.filter(status=Article.Status.PUBLISHED)
            .select_related('category', 'issue')
            .prefetch_related('authors', 'keywords')
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Kategoriyalar ro'yxati. SmallResultsPagination: 20/page."""

    permission_classes = [AllowAny]
    pagination_class = SmallResultsPagination
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """Mualliflar ro'yxati. SmallResultsPagination: 20/page."""

    permission_classes = [AllowAny]
    pagination_class = SmallResultsPagination
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'slug'
    search_fields = ['full_name', 'affiliation_uz']


class ConferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """Konferensiyalar ro'yxati. SmallResultsPagination: 20/page."""

    permission_classes = [AllowAny]
    pagination_class = SmallResultsPagination
    queryset = Conference.objects.all()
    serializer_class = ConferenceSerializer
    lookup_field = 'slug'
