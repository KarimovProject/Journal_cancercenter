from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .models import (
    Article,
    ArticleFigure,
    ArticleSupplementaryFile,
    Author,
    Category,
    Collection,
    Conference,
    EditorialBoardMember,
    Grant,
    Issue,
    JournalInfo,
    JournalMetric,
    JournalUpdate,
    Keyword,
    NewsletterSubscription,
    PostgraduateProgram,
    Reference,
    ScientificDepartment,
    StaticPage,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_en', 'order')
    list_editable = ('order',)
    search_fields = ('name_uz', 'name_ru', 'name_en')
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'academic_degree', 'affiliation_uz', 'orcid_id', 'email', 'user')
    search_fields = ('full_name', 'affiliation_uz', 'affiliation_ru', 'affiliation_en', 'orcid_id', 'user__username')
    prepopulated_fields = {'slug': ('full_name',)}
    fieldsets = (
        (None, {'fields': ('user', 'full_name', 'slug', 'photo', 'orcid_id', 'email', 'academic_degree', 'external_doctor_id')}),
        ('Lavozim / Affiliation', {'fields': ('affiliation_uz', 'affiliation_ru', 'affiliation_en')}),
        ('Biografiya', {'fields': ('bio_uz', 'bio_ru', 'bio_en')}),
    )


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year', 'published_date')
    list_filter = ('year',)
    search_fields = ('volume', 'number', 'year', 'title_uz')


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'full_text_uz': TinyMCE(),
            'full_text_ru': TinyMCE(),
            'full_text_en': TinyMCE(),
        }


class ArticleFigureInline(admin.TabularInline):
    model = ArticleFigure
    extra = 1
    fields = ('order', 'image', 'caption_uz', 'caption_ru', 'caption_en')


class ReferenceInline(admin.TabularInline):
    model = Reference
    extra = 1
    fields = ('order', 'citation_text', 'doi_or_url')


class SupplementaryFileInline(admin.TabularInline):
    model = ArticleSupplementaryFile
    extra = 1
    fields = ('order', 'file', 'title_uz', 'title_ru', 'title_en')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    inlines = (ArticleFigureInline, ReferenceInline, SupplementaryFileInline)
    list_display = ('title_uz', 'status', 'article_type', 'is_open_access', 'category', 'submitted_by', 'publication_date', 'views_count', 'citation_count')
    list_filter = ('status', 'article_type', 'is_open_access', 'category', 'issue', 'submitted_by', 'publication_date')
    search_fields = ('title_uz', 'title_ru', 'title_en', 'abstract_uz', 'doi')
    autocomplete_fields = ('authors', 'keywords', 'category', 'issue', 'corresponding_author')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'publication_date'
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'submitted_by')
    list_editable = ('status', 'article_type', 'is_open_access')
    fieldsets = (
        (None, {'fields': ('status', 'article_type', 'is_open_access', 'slug', 'category', 'issue', 'authors', 'corresponding_author', 'keywords')}),
        ('Sarlavha', {'fields': ('title_uz', 'title_ru', 'title_en')}),
        ('Annotatsiya', {'fields': ('abstract_uz', 'abstract_ru', 'abstract_en')}),
        ('To\'liq matn', {'fields': ('full_text_uz', 'full_text_ru', 'full_text_en'), 'classes': ('collapse',)}),
        ('Etika va moliyalashtirish', {
            'fields': (
                'funding_statement_uz', 'funding_statement_ru', 'funding_statement_en',
                'conflict_of_interest_uz', 'conflict_of_interest_ru', 'conflict_of_interest_en',
                'ethics_statement_uz', 'ethics_statement_ru', 'ethics_statement_en',
            ),
            'classes': ('collapse',),
        }),
        ('Fayl va metama\'lumot', {'fields': ('pdf_file', 'thumbnail_image', 'doi', 'pages', 'publication_date', 'citation_count')}),
        ('Statistika', {'fields': ('views_count', 'created_at', 'updated_at')}),
        ('Topshiruv', {'fields': ('submitted_by', 'rejection_reason')}),
    )


@admin.register(EditorialBoardMember)
class EditorialBoardMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position_uz', 'academic_degree', 'is_editor_in_chief', 'order')
    list_editable = ('is_editor_in_chief', 'order')
    list_filter = ('is_editor_in_chief',)
    search_fields = ('full_name', 'position_uz', 'academic_degree')


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'date_start', 'date_end', 'is_upcoming')
    list_filter = ('date_start',)
    search_fields = ('title_uz', 'title_ru', 'title_en')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'date_start'
    fieldsets = (
        (None, {'fields': ('slug', 'date_start', 'date_end', 'poster_image', 'program_pdf', 'registration_url')}),
        ('Sarlavha', {'fields': ('title_uz', 'title_ru', 'title_en')}),
        ('Tavsif', {'fields': ('description_uz', 'description_ru', 'description_en')}),
        ('Manzil', {'fields': ('location_uz', 'location_ru', 'location_en')}),
    )


@admin.register(ScientificDepartment)
class ScientificDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'head_of_department', 'order')
    list_editable = ('order',)
    search_fields = ('name_uz', 'name_ru', 'name_en')
    autocomplete_fields = ('head_of_department',)
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(PostgraduateProgram)
class PostgraduateProgramAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'program_type', 'deadline', 'is_active')
    list_filter = ('program_type', 'is_active')
    search_fields = ('title_uz', 'title_ru', 'title_en')


@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'funding_source', 'year', 'status')
    list_filter = ('status', 'year')
    search_fields = ('title_uz', 'title_ru', 'title_en', 'funding_source')
    autocomplete_fields = ('principal_investigators',)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('key', 'title_uz', 'updated_at')
    search_fields = ('key', 'title_uz')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'status', 'submission_deadline', 'order')
    list_editable = ('status', 'order')
    list_filter = ('status',)
    search_fields = ('title_uz', 'title_ru', 'title_en')
    autocomplete_fields = ('related_articles',)
    prepopulated_fields = {'slug': ('title_en',)}


@admin.register(JournalMetric)
class JournalMetricAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'value', 'year', 'order')
    list_editable = ('value', 'order')


@admin.register(JournalUpdate)
class JournalUpdateAdmin(admin.ModelAdmin):
    list_display = ('title_uz', 'published_date', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'published_date')
    search_fields = ('title_uz', 'title_ru', 'title_en')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'published_date'


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_confirmed', 'is_active', 'created_at')
    list_filter = ('is_confirmed', 'is_active', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'confirm_token')


@admin.register(JournalInfo)
class JournalInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'issn_print', 'issn_online')

    def has_add_permission(self, request):
        # Singleton: faqat bitta yozuv.
        return not JournalInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Oncoscience — Ilmiy jurnal boshqaruvi"
admin.site.site_title = "Oncoscience admin"
admin.site.index_title = "Kontent boshqaruvi"
