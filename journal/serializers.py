from rest_framework import serializers

from .models import Article, Author, Category, Conference, Issue


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'name_uz', 'name_ru', 'name_en']


class AuthorSerializer(serializers.ModelSerializer):
    affiliation = serializers.CharField(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'slug', 'full_name', 'affiliation', 'photo', 'orcid_id']


class IssueSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'volume', 'number', 'year', 'title', 'cover_image', 'published_date']


class ArticleListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)
    abstract = serializers.CharField(read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'abstract', 'authors', 'category',
            'article_type', 'article_type_display', 'is_open_access', 'thumbnail_image',
            'doi', 'publication_date', 'views_count', 'citation_count', 'url',
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        path = obj.get_absolute_url()
        return request.build_absolute_uri(path) if request else path


class ArticleDetailSerializer(ArticleListSerializer):
    issue = IssueSerializer(read_only=True)
    keywords = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    pdf_file = serializers.FileField(read_only=True)
    citation_apa = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + [
            'title_uz', 'title_ru', 'title_en',
            'abstract_uz', 'abstract_ru', 'abstract_en',
            'issue', 'keywords', 'pdf_file', 'pages', 'citation_apa',
        ]

    def get_citation_apa(self, obj):
        return obj.citation_apa()


class ConferenceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Conference
        fields = [
            'id', 'slug', 'title', 'description', 'location',
            'date_start', 'date_end', 'poster_image', 'registration_url', 'is_upcoming',
        ]
