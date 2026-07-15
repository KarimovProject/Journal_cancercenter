from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import ArticleSubmissionForm, AuthorProfileForm, RegistrationForm
from .filters import ArticleFilter
from .models import (
    Article,
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
    NewsletterSubscription,
    PostgraduateProgram,
    ScientificDepartment,
    StaticPage,
)

PUBLISHED = Article.Status.PUBLISHED


def _rate_limited(request, key_prefix, limit=5, window=3600):
    """Simple IP-based rate limiter backed by the cache.

    Returns True if the caller has exceeded ``limit`` requests within
    ``window`` seconds for the given ``key_prefix``.
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip = ip.split(',')[0].strip() if ip else request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'ratelimit:{key_prefix}:{ip}'
    count = cache.get(cache_key, 0)
    if count >= limit:
        return True
    cache.set(cache_key, count + 1, window)
    return False


def _published_articles():
    return (
        Article.objects.filter(status=PUBLISHED)
        .select_related('category', 'issue')
        .prefetch_related('authors')
    )


def home(request):
    articles = _published_articles()
    context = {
        'latest_articles': articles[:5],
        'most_viewed': articles.order_by('-views_count')[:5],
        'categories': Category.objects.all(),
        'editor_in_chief': EditorialBoardMember.objects.filter(is_editor_in_chief=True).first(),
        'metrics': JournalMetric.objects.all(),
        'collections': Collection.objects.filter(status=Collection.Status.OPEN)[:3],
        'journal_updates': JournalUpdate.objects.filter(is_published=True)[:3],
        'upcoming_conferences': Conference.objects.filter(
            date_start__gte=timezone.now().date()
        ).order_by('date_start')[:3],
        'latest_issue': Issue.objects.first(),
        'stats': {
            'articles': articles.count(),
            'authors': Author.objects.count(),
            'categories': Category.objects.count(),
            'editors': EditorialBoardMember.objects.count(),
        },
        'meta_description': 'Respublika Ixtisoslashtirilgan Onkologiya va Radiologiya '
                            'Ilmiy-Amaliy Tibbiyot Markazi ilmiy nashrlari platformasi.',
    }
    return render(request, 'journal/home.html', context)


@require_POST
def newsletter_subscribe(request):
    """'Sign up for alerts' — double opt-in orqali email tasdiqlash."""
    email = (request.POST.get('email') or '').strip().lower()
    next_url = request.POST.get('next') or reverse('journal:home')

    if _rate_limited(request, 'newsletter', limit=5, window=3600):
        messages.error(request, _('Juda ko\'p urinish. Iltimos, birozdan so\'ng qayta urining.'))
        return redirect(next_url)

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, _("Iltimos, to'g'ri email manzil kiriting."))
        return redirect(next_url)

    obj, created = NewsletterSubscription.objects.get_or_create(email=email)
    if obj.is_confirmed:
        messages.info(request, _('Bu email allaqachon obuna bo\'lgan.'))
        return redirect(next_url)

    # (Re)generate token and send confirmation email.
    obj.confirm_token = NewsletterSubscription.generate_token()
    obj.is_active = False
    obj.save(update_fields=['confirm_token', 'is_active'])

    site_name = getattr(settings, 'SITE_NAME', 'Oncoscience')
    site_domain = getattr(settings, 'SITE_DOMAIN', 'http://localhost:8000')
    confirm_url = f"{site_domain}{reverse('journal:newsletter_confirm', args=[obj.confirm_token])}"
    send_mail(
        f'[{site_name}] Obunani tasdiqlang',
        (
            f'Assalomu alaykum,\n\n'
            f'{site_name} yangiliklariga obuna bo\'lish uchun quyidagi havolani bosing:\n'
            f'{confirm_url}\n\n'
            f'Agar bu siz bo\'lmasangiz, ushbu xatni e\'tiborsiz qoldiring.'
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True,
    )
    messages.success(request, _('Tasdiqlash havolasi emailingizga yuborildi. Iltimos, pochtangizni tekshiring.'))
    return redirect(next_url)


def newsletter_confirm(request, token):
    """Confirm a newsletter subscription via the emailed token."""
    obj = NewsletterSubscription.objects.filter(confirm_token=token).first()
    if not obj:
        messages.error(request, _('Tasdiqlash havolasi yaroqsiz yoki muddati o\'tgan.'))
        return redirect('journal:home')
    obj.is_confirmed = True
    obj.is_active = True
    obj.confirm_token = ''
    obj.save(update_fields=['is_confirmed', 'is_active', 'confirm_token'])
    messages.success(request, _('Obunangiz tasdiqlandi! Yangi maqolalar haqida xabar beramiz.'))
    return redirect('journal:home')


def update_list(request):
    updates = JournalUpdate.objects.filter(is_published=True)
    context = {
        'updates': updates,
        'meta_description': 'Jurnal yangiliklari va e\'lonlari.',
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
        'collections': Collection.objects.all(),
        'meta_description': 'Call for papers — mavzuli to\'plamlar.',
    }
    return render(request, 'journal/collection_list.html', context)


def collection_detail(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    context = {
        'collection': collection,
        'articles': collection.related_articles.filter(status=PUBLISHED),
        'meta_description': (collection.description or collection.title)[:300],
    }
    return render(request, 'journal/collection_detail.html', context)


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
        'categories': Category.objects.all(),
        'years': (
            _published_articles()
            .dates('publication_date', 'year', order='DESC')
        ),
        'total': filtered.count(),
        'querystring': querydict.urlencode(),
        'current_sort': ordering,
        'meta_description': 'Onkologiya va radiologiya sohasidagi ilmiy maqolalar to\'plami.',
    }
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

    # Increment views without touching updated_at.
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


def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    articles = _published_articles().filter(authors=author)
    total_views = sum(a.views_count for a in articles)
    total_citations = sum(a.citation_count for a in articles)
    context = {
        'author': author,
        'articles': articles,
        'total_views': total_views,
        'total_citations': total_citations,
        'meta_description': f'{author.full_name} — {author.affiliation}'.strip(' —'),
    }
    return render(request, 'journal/author_detail.html', context)


def issue_list(request):
    context = {
        'issues': Issue.objects.all(),
        'meta_description': 'Jurnal sonlari arxivi.',
    }
    return render(request, 'journal/issue_list.html', context)


def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    articles = _published_articles().filter(issue=issue)
    context = {
        'issue': issue,
        'articles': articles,
        'meta_description': f'{issue} — maqolalar to\'plami.',
    }
    return render(request, 'journal/issue_detail.html', context)


def editorial_board(request):
    context = {
        'members': EditorialBoardMember.objects.all(),
        'meta_description': 'Ilmiy kengash a\'zolari.',
    }
    return render(request, 'journal/editorial_board.html', context)


def department_list(request):
    context = {
        'departments': ScientificDepartment.objects.select_related('head_of_department'),
        'meta_description': 'Ilmiy kafedralar ro\'yxati.',
    }
    return render(request, 'journal/department_list.html', context)


def conference_list(request):
    today = timezone.now().date()
    all_conf = Conference.objects.all()
    context = {
        'upcoming': all_conf.filter(Q(date_end__gte=today) | Q(date_end__isnull=True, date_start__gte=today)).order_by('date_start'),
        'past': all_conf.filter(Q(date_end__lt=today) | Q(date_end__isnull=True, date_start__lt=today)).order_by('-date_start'),
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
        'meta_description': f'{labels.get(program_type, "")} dasturlari haqida ma\'lumot.',
    }
    return render(request, 'journal/postgraduate.html', context)


def grant_list(request):
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
    """'Mualliflar uchun' — StaticPage bo'lsa undan, aks holda default matn."""
    page = StaticPage.objects.filter(key='for-authors').first()
    context = {
        'page': page,
        'meta_description': 'Maqola yuborish qoidalari va talablari.',
    }
    return render(request, 'journal/for_authors.html', context)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('journal:home')
    if request.method == 'POST':
        if _rate_limited(request, 'register', limit=10, window=3600):
            messages.error(request, _('Juda ko\'p urinish. Iltimos, birozdan so\'ng qayta urining.'))
            return render(request, 'journal/auth/register.html', {'form': RegistrationForm()})
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, _('Hisobingiz muvaffaqiyatli yaratildi!'))
            return redirect('journal:home')
    else:
        form = RegistrationForm()
    return render(request, 'journal/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('journal:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, _('Xush kelibsiz, {}!').format(user.username))
            next_url = request.POST.get('next') or reverse('journal:home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'journal/auth/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    messages.info(request, _('Tizimdan chiqdingiz.'))
    return redirect('journal:home')


# ---------------------------------------------------------------------------
# Article submission
# ---------------------------------------------------------------------------

@login_required(login_url='/ilm-fan/kirish/')
def submit_article(request):
    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.submitted_by = request.user
            article.status = Article.Status.DRAFT

            # Parse issue_text (e.g. "Vol. 5, No. 2, 2025") and link/create Issue
            issue_text = form.cleaned_data.get('issue_text', '').strip()
            if issue_text:
                import re
                m = re.match(
                    r'Vol\.?\s*(\d+).*?No\.?\s*(\d+).*?(\d{4})',
                    issue_text, re.IGNORECASE,
                )
                if m:
                    vol, num, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    issue_obj, _created = Issue.objects.get_or_create(
                        volume=vol, number=num, year=yr,
                    )
                    article.issue = issue_obj

            article.save()
            # Auto-link the user's author profile as an author of this article
            author = Author.objects.filter(user=request.user).first()
            if author:
                article.authors.add(author)
            # Process co-authors (one per line -> create/find Author objects)
            co_authors_text = form.cleaned_data.get('co_authors', '')
            if co_authors_text:
                for line in co_authors_text.split('\n'):
                    name = line.strip()
                    if name:
                        co_author, _created = Author.objects.get_or_create(
                            full_name=name,
                            defaults={'slug': name.lower().replace(' ', '-')[:280]},
                        )
                        article.authors.add(co_author)
            # Process keywords (comma-separated text -> Keyword objects)
            keywords_text = form.cleaned_data.get('keywords_text', '')
            if keywords_text:
                from .models import Keyword
                for kw in keywords_text.split(','):
                    kw = kw.strip()
                    if kw:
                        keyword_obj, _created = Keyword.objects.get_or_create(name=kw)
                        article.keywords.add(keyword_obj)
            messages.success(request, _('Maqolangiz qabul qilindi! Tahririyat koʻrib chiqgach, natija haqida xabar beradi.'))
            return redirect('journal:my_articles')
    else:
        form = ArticleSubmissionForm()
    context = {
        'form': form,
        'meta_description': _('Maqola topshirish formasi.'),
    }
    return render(request, 'journal/submit_article.html', context)


@login_required(login_url='/ilm-fan/kirish/')
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.submitted_by != request.user:
        raise Http404()
    if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED, Article.Status.REVIEW):
        messages.error(request, _('Chop etilgan maqolani tahrirlash mumkin emas.'))
        return redirect('journal:my_articles')

    # Pre-fill keywords and co-authors
    initial = {}
    if article.keywords.exists():
        initial['keywords_text'] = ', '.join(k.name for k in article.keywords.all())
    if article.issue:
        initial['issue_text'] = f'Vol. {article.issue.volume}, No. {article.issue.number}, {article.issue.year}'
    # Co-authors: all authors except the current user's own profile
    other_authors = article.authors.exclude(user=request.user)
    if other_authors.exists():
        initial['co_authors'] = '\n'.join(a.full_name for a in other_authors)

    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES, instance=article, initial=initial)
        if form.is_valid():
            article = form.save(commit=False)
            article.status = Article.Status.DRAFT
            article.rejection_reason = ''

            issue_text = form.cleaned_data.get('issue_text', '').strip()
            if issue_text:
                import re
                m = re.match(r'Vol\.?\s*(\d+).*?No\.?\s*(\d+).*?(\d{4})', issue_text, re.IGNORECASE)
                if m:
                    vol, num, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    issue_obj, _created = Issue.objects.get_or_create(volume=vol, number=num, year=yr)
                    article.issue = issue_obj

            article.save()

            # Re-link the user's own author profile
            author = Author.objects.filter(user=request.user).first()
            article.authors.set([author] if author else [])

            # Process co-authors
            co_authors_text = form.cleaned_data.get('co_authors', '')
            if co_authors_text:
                for line in co_authors_text.split('\n'):
                    name = line.strip()
                    if name:
                        co_author, _created = Author.objects.get_or_create(
                            full_name=name,
                            defaults={'slug': name.lower().replace(' ', '-')[:280]},
                        )
                        article.authors.add(co_author)

            # Update keywords
            article.keywords.clear()
            keywords_text = form.cleaned_data.get('keywords_text', '')
            if keywords_text:
                from .models import Keyword
                for kw in keywords_text.split(','):
                    kw = kw.strip()
                    if kw:
                        keyword_obj, _created = Keyword.objects.get_or_create(name=kw)
                        article.keywords.add(keyword_obj)

            messages.success(request, _('Maqola yangilandi va qayta ko\'rib chiqishga yuborildi.'))
            return redirect('journal:my_articles')
    else:
        form = ArticleSubmissionForm(instance=article, initial=initial)

    context = {
        'form': form,
        'article': article,
        'is_edit': True,
        'meta_description': _('Maqolani tahrirlash.'),
    }
    return render(request, 'journal/submit_article.html', context)


@login_required(login_url='/ilm-fan/kirish/')
def my_articles(request):
    articles = Article.objects.filter(submitted_by=request.user).order_by('-created_at')
    stats = {
        'total': articles.count(),
        'published': articles.filter(status=Article.Status.PUBLISHED).count(),
        'draft': articles.filter(status=Article.Status.DRAFT).count(),
        'review': articles.filter(status=Article.Status.REVIEW).count(),
        'rejected': articles.filter(status=Article.Status.REJECTED).count(),
        'total_views': sum(a.views_count for a in articles),
        'total_citations': sum(a.citation_count for a in articles),
    }
    context = {
        'articles': articles,
        'stats': stats,
        'meta_description': _('Mening maqolalarim.'),
    }
    return render(request, 'journal/my_articles.html', context)


@login_required(login_url='/ilm-fan/kirish/')
def edit_profile(request):
    author = getattr(request.user, 'author_profile', None)
    if not author:
        author = Author.objects.create(user=request.user, full_name=request.user.get_full_name() or request.user.username)

    if request.method == 'POST':
        form = AuthorProfileForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profilingiz yangilandi.'))
            return redirect('journal:edit_profile')
    else:
        form = AuthorProfileForm(instance=author)

    context = {
        'form': form,
        'author': author,
        'meta_description': _('Profilni tahrirlash.'),
    }
    return render(request, 'journal/edit_profile.html', context)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

def custom_404(request, exception=None):
    return render(request, 'journal/404.html', status=404)


def custom_500(request):
    return render(request, 'journal/500.html', status=500)
