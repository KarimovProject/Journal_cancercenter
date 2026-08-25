"""
journal/views/public.py

Ommaviy sahifalar: home, article_list, article_detail,
issue, author, editorial_board, conference, grant, va boshqalar.
"""
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, F, Count, Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from ..filters import ArticleFilter
from ..forms import FeatureRequestForm
from ..models import (
    Article,
    Author,
    Category,
    Collection,
    Conference,
    EditorialBoardMember,
    Grant,
    Issue,
    JournalMetric,
    JournalUpdate,
    PostgraduateProgram,
    ScientificDepartment,
    StaticPage,
)

PUBLISHED = Article.Status.PUBLISHED


def _published_articles():
    """
    Barcha joylarda ishlatiladigan asosiy published maqolalar queryset'i.
    select_related + prefetch_related + defer orqali N+1 muammolari oldini oladi.
    """
    return (
        Article.objects.filter(status=PUBLISHED)
        .select_related('category', 'issue')
        .prefetch_related('authors')
        .defer('full_text_uz', 'full_text_ru', 'full_text_en')
    )


def home(request):
    context = cache.get('homepage_context')
    if not context:
        articles = _published_articles()
        context = {
            'latest_articles': list(articles[:5]),
            'most_viewed': list(articles.order_by('-views_count')[:5]),
            # ORM: annotate bilan har bir kategoriyada nechtа maqola borligini hisoblaymiz
            # Bu bitta qo'shimcha so'rov saqlab, shablondagi .count() chaqiruvlarini yo'qotadi
            'categories': list(
                Category.objects.annotate(article_count=Count('articles'))
            ),
            'editor_in_chief': (
                EditorialBoardMember.objects
                .select_related()  # kelajakdagi FK uchun
                .filter(role=EditorialBoardMember.Role.EDITOR_IN_CHIEF)
                .first()
            ),
            'metrics': list(JournalMetric.objects.all()),
            'collections': list(
                Collection.objects
                .filter(status=Collection.Status.OPEN)
                .prefetch_related('related_articles')[:3]
            ),
            'journal_updates': list(JournalUpdate.objects.filter(is_published=True)[:3]),
            'upcoming_conferences': list(
                Conference.objects
                .filter(date_start__gte=timezone.now().date())
                .order_by('date_start')[:3]
            ),
            # ORM: prefetch_related bilan issue sahifasida N+1 oldini olamiz
            'latest_issue': (
                Issue.objects
                .prefetch_related(
                    Prefetch(
                        'articles',
                        queryset=_published_articles(),
                        to_attr='published_articles_list',
                    )
                )
                .first()
            ),
            'stats': {
                'articles': articles.count(),
                'authors': Author.objects.count(),
                'categories': Category.objects.count(),
                'editors': EditorialBoardMember.objects.count(),
            },
            'meta_description': (
                'Respublika Ixtisoslashtirilgan Onkologiya va Radiologiya '
                'Ilmiy-Amaliy Tibbiyot Markazi ilmiy nashrlari platformasi.'
            ),
        }
        cache.set('homepage_context', context, 60 * 15)
    return render(request, 'journal/home.html', context)


def article_list(request):
    qs = _published_articles()
    f = ArticleFilter(request.GET, queryset=qs)
    filtered = f.qs

    ordering = request.GET.get('sort', '-publication_date')
    allowed = {'-publication_date', 'publication_date', '-views_count', '-citation_count', 'title_uz'}
    if ordering in allowed:
        filtered = filtered.order_by(ordering)

    paginator = Paginator(filtered, 9)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    querydict = request.GET.copy()
    querydict.pop('page', None)

    context = {
        'articles': articles,
        'filter': f,
        # ORM: annotate — shablonda category.article_count ishlatiladigan bo'lsa N+1 yo'q
        'categories': Category.objects.annotate(article_count=Count('articles')),
        'years': _published_articles().dates('publication_date', 'year', order='DESC'),
        'total': filtered.count(),
        'querystring': querydict.urlencode(),
        'current_sort': ordering,
        'meta_description': 'Onkologiya va radiologiya sohasidagi ilmiy maqolalar toʻplami.',
    }

    # HTMX: faqat qidiruv/filtr orqali kelgan so'rovlar uchun qisqartirilgan fragmentni qaytaramiz.
    # Agar HX-Boost orqali (navigatsiya) kelgan bo'lsa, to'liq sahifa kerak.
    if request.headers.get('HX-Target') == 'articles-wrapper':
        return render(request, 'journal/partials/_article_results.html', context)

    return render(request, 'journal/article_list.html', context)



def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects
        .select_related('category', 'issue', 'corresponding_author')
        .prefetch_related('authors', 'keywords', 'figures', 'references', 'supplementary_files'),
        slug=slug,
    )
    if not article.is_published and not request.user.is_staff:
        raise Http404()

    # ORM: F() expression — Python'ga yuklamay, to'g'ridan-to'g'ri DBda hisoblanadi
    Article.objects.filter(pk=article.pk).update(views_count=F('views_count') + 1)
    article.views_count += 1

    related = (
        _published_articles()
        .filter(category=article.category)
        .exclude(pk=article.pk)[:4]
    )
    context = {
        'article': article,
        'related_articles': related,
        'meta_description': (article.abstract or article.title)[:300],
        'og_type': 'article',
    }
    return render(request, 'journal/article_detail.html', context)


def download_citation(request, slug, format):
    article = get_object_or_404(Article, slug=slug)
    if format == 'ris':
        content = article.citation_ris()
        content_type = 'application/x-research-info-systems'
        ext = 'ris'
    else:
        method = getattr(article, f"citation_{format}", None)
        if not method:
            raise Http404("Citation format not supported.")
        content = method()
        content_type = 'text/plain; charset=utf-8'
        ext = 'txt'

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="citation_{article.slug}.{ext}"'
    return response


def author_detail(request, slug):
    from django.db.models import Sum
    author = get_object_or_404(
        Author.objects.select_related('user'),
        slug=slug,
    )
    articles = _published_articles().filter(authors=author)
    agg = articles.aggregate(
        total_views=Sum('views_count'),
        total_citations=Sum('citation_count'),
    )
    context = {
        'author': author,
        'articles': articles,
        'total_views': agg['total_views'] or 0,
        'total_citations': agg['total_citations'] or 0,
        'meta_description': f'{author.full_name} — {author.affiliation}'.strip(' —'),
    }
    return render(request, 'journal/author_detail.html', context)


def issue_list(request):
    context = {
        # ORM: annotate — shablonda `issue.article_count` ishlatilganda N+1 yo'q
        'issues': Issue.objects.annotate(article_count=Count('article')),
        'meta_description': 'Jurnal sonlari arxivi.',
    }
    return render(request, 'journal/issue_list.html', context)


def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    # ORM: _published_articles() allaqachon select_related/prefetch_related qo'llagan
    articles = _published_articles().filter(issue=issue)
    context = {
        'issue': issue,
        'articles': articles,
        'meta_description': f'{issue} — maqolalar toʻplami.',
    }
    return render(request, 'journal/issue_detail.html', context)


def editorial_board(request):
    context = {
        # ORM: select_related — a'zoning bog'liq ma'lumotlari uchun N+1 yo'q
        'members': EditorialBoardMember.objects.select_related().order_by('role', 'order'),
        'meta_description': "Ilmiy kengash aʼzolari.",
    }
    return render(request, 'journal/editorial_board.html', context)


def department_list(request):
    context = {
        'departments': ScientificDepartment.objects.select_related('head_of_department'),
        'meta_description': "Ilmiy kafedralar roʻyxati.",
    }
    return render(request, 'journal/department_list.html', context)


def conference_list(request):
    today = timezone.now().date()
    all_conf = Conference.objects.all()
    context = {
        'upcoming': all_conf.filter(
            Q(date_end__gte=today) | Q(date_end__isnull=True, date_start__gte=today)
        ).order_by('date_start'),
        'past': all_conf.filter(
            Q(date_end__lt=today) | Q(date_end__isnull=True, date_start__lt=today)
        ).order_by('-date_start'),
        'meta_description': 'Konferensiyalar va ilmiy tadbirlar.',
    }
    return render(request, 'journal/conference_list.html', context)


def conference_detail(request, slug):
    conference = get_object_or_404(Conference, slug=slug)
    context = {
        'conference': conference,
        'meta_description': (conference.description or conference.title)[:300],
    }
    return render(request, 'journal/conference_detail.html', context)


def postgraduate(request, program_type):
    if program_type not in dict(PostgraduateProgram.ProgramType.choices):
        raise Http404()
    programs = PostgraduateProgram.objects.filter(program_type=program_type, is_active=True)
    labels = {'aspirantura': 'Aspirantura', 'ordinatura': 'Ordinatura'}
    context = {
        'programs': programs,
        'program_type': program_type,
        'page_title': labels.get(program_type, program_type.title()),
        'meta_description': f'{labels.get(program_type, "")} dasturlari haqida maʼlumot.',
    }
    return render(request, 'journal/postgraduate.html', context)


def grant_list(request):
    # ORM: prefetch_related — grant'ning principal_investigators'lari uchun N+1 yo'q
    grants = Grant.objects.prefetch_related('principal_investigators')
    context = {
        'active_grants': grants.filter(status=Grant.Status.ACTIVE),
        'completed_grants': grants.filter(status=Grant.Status.COMPLETED),
        'meta_description': 'Grantlar va ilmiy loyihalar.',
    }
    return render(request, 'journal/grant_list.html', context)


def static_page(request, key):
    page = get_object_or_404(StaticPage, key=key)
    context = {
        'page': page,
        'meta_description': page.title,
    }
    return render(request, 'journal/static_page.html', context)


def for_authors(request):
    "'Mualliflar uchun' — StaticPage boʻlsa undan, aks holda default matn."
    page = StaticPage.objects.filter(key='for-authors').first()
    context = {
        'page': page,
        'meta_description': 'Maqola yuborish qoidalari va talablari.',
    }
    return render(request, 'journal/for_authors.html', context)


def update_list(request):
    updates = JournalUpdate.objects.filter(is_published=True)
    context = {
        'updates': updates,
        'meta_description': "Jurnal yangiliklari va eʼlonlari.",
    }
    return render(request, 'journal/update_list.html', context)


def update_detail(request, slug):
    update = get_object_or_404(JournalUpdate, slug=slug, is_published=True)
    context = {
        'update': update,
        'meta_description': (update.content or update.title)[:300],
    }
    return render(request, 'journal/update_detail.html', context)


def collection_list(request):
    context = {
        # ORM: prefetch_related — har bir to'plamdagi maqolalar uchun N+1 yo'q
        'collections': Collection.objects.prefetch_related('related_articles'),
        'meta_description': "Call for papers — mavzuli toʻplamlar.",
    }
    return render(request, 'journal/collection_list.html', context)


def collection_detail(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    context = {
        'collection': collection,
        'articles': (
            collection.related_articles
            .filter(status=PUBLISHED)
            .select_related('category', 'issue')
            .prefetch_related('authors')
        ),
        'meta_description': (collection.description or collection.title)[:300],
    }
    return render(request, 'journal/collection_detail.html', context)


def feedback_view(request):
    if request.method == 'POST':
        form = FeatureRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Taklifingiz muvaffaqiyatli yuborildi. Rahmat!')
            form = FeatureRequestForm()
    else:
        form = FeatureRequestForm()

    return render(request, 'journal/feedback.html', {'form': form})


def custom_404(request, exception=None):
    return render(request, 'journal/404.html', status=404)


def custom_500(request):
    return render(request, 'journal/500.html', status=500)
