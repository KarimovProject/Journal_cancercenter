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
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from ipware import get_client_ip

from .forms import (
    ArticleFigureFormSet,
    ArticleSubmissionForm,
    ArticleSupplementaryFileFormSet,
    AuthorProfileForm,
    ReferenceFormSet,
    RegistrationForm,
)
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
    Review,
    ScientificDepartment,
    StaticPage,
)

PUBLISHED = Article.Status.PUBLISHED


def _rate_limited(request, key_prefix, limit=5, window=3600):
    """Simple IP-based rate limiter backed by the cache."""
    client_ip, is_routable = get_client_ip(request)
    ip = client_ip or 'unknown'
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
        ref_fs = ReferenceFormSet(request.POST, prefix='ref', instance=form.instance)
        fig_fs = ArticleFigureFormSet(request.POST, request.FILES, prefix='fig', instance=form.instance)
        supp_fs = ArticleSupplementaryFileFormSet(request.POST, request.FILES, prefix='supp', instance=form.instance)

        if form.is_valid() and ref_fs.is_valid() and fig_fs.is_valid() and supp_fs.is_valid():
            with transaction.atomic():
                article = form.save(commit=False)
                article.submitted_by = request.user
                article.status = Article.Status.DRAFT
                article.save()

                form.save_m2m_custom(article, request.user)

                for fs in (ref_fs, fig_fs, supp_fs):
                    fs.instance = article
                    fs.save()

            messages.success(request, _('Maqolangiz qabul qilindi! Tahririyat koʻrib chiqgach, natija haqida xabar beradi.'))
            return redirect('journal:my_articles')
    else:
        form = ArticleSubmissionForm()
        ref_fs = ReferenceFormSet(prefix='ref', instance=Article())
        fig_fs = ArticleFigureFormSet(prefix='fig', instance=Article())
        supp_fs = ArticleSupplementaryFileFormSet(prefix='supp', instance=Article())

    context = {
        'form': form,
        'ref_fs': ref_fs,
        'fig_fs': fig_fs,
        'supp_fs': supp_fs,
        'meta_description': _('Maqola topshirish formasi.'),
    }
    return render(request, 'journal/submit_article.html', context)


@login_required(login_url='/ilm-fan/kirish/')
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.submitted_by != request.user:
        raise Http404()
    if article.status not in (Article.Status.DRAFT, Article.Status.REJECTED):
        messages.error(request, _('Koʻrib chiqilayotgan yoki chop etilgan maqolani tahrirlash mumkin emas.'))
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
        ref_fs = ReferenceFormSet(request.POST, prefix='ref', instance=article)
        fig_fs = ArticleFigureFormSet(request.POST, request.FILES, prefix='fig', instance=article)
        supp_fs = ArticleSupplementaryFileFormSet(request.POST, request.FILES, prefix='supp', instance=article)

        if form.is_valid() and ref_fs.is_valid() and fig_fs.is_valid() and supp_fs.is_valid():
            with transaction.atomic():
                article = form.save(commit=False)
                article.status = Article.Status.DRAFT
                article.rejection_reason = ''
                article.save()

                form.save_m2m_custom(article, request.user, is_edit=True)

                for fs in (ref_fs, fig_fs, supp_fs):
                    fs.save()

            messages.success(request, _('Maqola yangilandi va qayta ko\'rib chiqishga yuborildi.'))
            return redirect('journal:my_articles')
    else:
        form = ArticleSubmissionForm(instance=article, initial=initial)
        ref_fs = ReferenceFormSet(prefix='ref', instance=article)
        fig_fs = ArticleFigureFormSet(prefix='fig', instance=article)
        supp_fs = ArticleSupplementaryFileFormSet(prefix='supp', instance=article)

    context = {
        'form': form,
        'ref_fs': ref_fs,
        'fig_fs': fig_fs,
        'supp_fs': supp_fs,
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
# Peer Review
# ---------------------------------------------------------------------------

@login_required(login_url='/ilm-fan/kirish/')
def reviewer_dashboard(request):
    # Mark all unread reviewer notifications as read when they visit the dashboard
    from .models import Notification
    Notification.objects.filter(
        user=request.user, 
        link__contains='taqriz-paneli', 
        is_read=False
    ).update(is_read=True)

    reviews = Review.objects.filter(reviewer=request.user).select_related('article')
    pending_reviews = reviews.filter(decision=Review.Decision.PENDING)
    completed_reviews = reviews.exclude(decision=Review.Decision.PENDING)
    
    context = {
        'pending_reviews': pending_reviews,
        'completed_reviews': completed_reviews,
        'meta_description': _('Taqrizchi paneli.'),
    }
    return render(request, 'journal/reviewer_dashboard.html', context)

@login_required(login_url='/ilm-fan/kirish/')
def review_article(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    from .forms import ReviewForm
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            
            # Mark reviewer's notifications related to reviewer dashboard as read
            from .models import Notification
            Notification.objects.filter(
                user=request.user,
                link__contains='taqriz-paneli',
                is_read=False
            ).update(is_read=True)

            messages.success(request, _('Taqriz muvaffaqiyatli saqlandi!'))
            return redirect('journal:reviewer_dashboard')
    else:
        form = ReviewForm(instance=review)
        
    context = {
        'review': review,
        'article': review.article,
        'form': form,
        'meta_description': _('Maqolani taqrizlash.'),
    }
    return render(request, 'journal/review_article.html', context)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

def custom_404(request, exception=None):
    return render(request, 'journal/404.html', status=404)


def custom_500(request):
    return render(request, 'journal/500.html', status=500)

from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncMonth

@staff_member_required
def admin_stats_api(request):
    # Statuses
    status_counts = Article.objects.values('status').annotate(count=Count('id'))
    status_data = {item['status']: item['count'] for item in status_counts}
    
    # Monthly submissions (last 6 months or all)
    monthly = Article.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
    months_labels = [m['month'].strftime('%b %Y') if m['month'] else 'Unknown' for m in monthly]
    months_data = [m['count'] for m in monthly]
    
    return JsonResponse({
        'statuses': status_data,
        'months': {
            'labels': months_labels,
            'data': months_data
        }
    })
