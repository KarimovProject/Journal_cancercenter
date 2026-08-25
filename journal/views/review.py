"""
journal/views/review.py

Taqrizchi va muharrir panellari.
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from ..models import Article, Author, Review

User = get_user_model()


def is_editor(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@login_required
def read_notification(request, notif_id):
    from ..models import Notification
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    if notif.link:
        return redirect(notif.link)
    return redirect('journal:home')


# ---------------------------------------------------------------------------
# Peer Review
# ---------------------------------------------------------------------------

@login_required
def reviewer_dashboard(request):
    from ..models import Notification
    Notification.objects.filter(
        user=request.user,
        link__contains='taqriz-paneli',
        is_read=False,
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


@login_required
def review_article(request, pk):
    review = get_object_or_404(
        Review.objects.select_related('article', 'reviewer'),
        pk=pk,
        reviewer=request.user,
    )
    from ..forms import ReviewForm
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            from ..models import Notification
            Notification.objects.filter(
                user=request.user,
                link__contains='taqriz-paneli',
                is_read=False,
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
# Admin stats API
# ---------------------------------------------------------------------------

@staff_member_required
def admin_stats_api(request):
    total_articles = Article.objects.count()
    total_authors = Author.objects.count()
    pending_reviews = Review.objects.filter(decision=Review.Decision.PENDING).count()
    total_views = Article.objects.aggregate(total=Sum('views_count'))['total'] or 0

    status_counts = Article.objects.values('status').annotate(count=Count('id'))
    status_data = {item['status']: item['count'] for item in status_counts}

    monthly = (
        Article.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    months_labels = [m['month'].strftime('%b %Y') if m['month'] else 'Unknown' for m in monthly]
    months_data = [m['count'] for m in monthly]

    return JsonResponse({
        'summary': {
            'total_articles': total_articles,
            'total_authors': total_authors,
            'pending_reviews': pending_reviews,
            'total_views': total_views,
        },
        'statuses': status_data,
        'months': {
            'labels': months_labels,
            'data': months_data,
        }
    })


# ---------------------------------------------------------------------------
# Editorial Dashboard
# ---------------------------------------------------------------------------

@user_passes_test(is_editor)
def editor_dashboard(request):
    articles = (
        Article.objects
        .select_related('category', 'issue', 'submitted_by')
        .prefetch_related('authors')
        .order_by('-created_at')
    )
    # FIX: Article.Status enum ishlatildi — string literal emas
    stats = {
        'new_submissions': articles.filter(status=Article.Status.DRAFT).count(),
        'under_review': articles.filter(status=Article.Status.REVIEW).count(),
        'published': articles.filter(status=Article.Status.PUBLISHED).count(),
        'rejected': articles.filter(status=Article.Status.REJECTED).count(),
    }
    context = {
        'articles': articles,
        'stats': stats,
    }
    return render(request, 'journal/dashboard/editor_dashboard.html', context)


@user_passes_test(is_editor)
def editor_article_detail(request, pk):
    article = get_object_or_404(
        Article.objects
        .select_related('category', 'issue', 'corresponding_author', 'submitted_by')
        .prefetch_related('authors', 'keywords', 'figures', 'references'),
        pk=pk,
    )
    reviews = (
        Review.objects
        .filter(article=article)
        .select_related('reviewer')
        .order_by('-created_at')
    )
    context = {
        'article': article,
        'reviews': reviews,
    }
    return render(request, 'journal/dashboard/editor_article_detail.html', context)


@user_passes_test(is_editor)
def editor_assign_reviewer(request, pk):
    article = get_object_or_404(Article, pk=pk)
    # ORM: select_related va exclude — maqola mualliflari taqrizchi bo'la olmaydi
    author_user_ids = article.authors.filter(
        user__isnull=False
    ).values_list('user_id', flat=True)

    users = (
        User.objects
        .filter(is_active=True)
        .exclude(id__in=author_user_ids)
        .order_by('first_name', 'username')
    )

    if request.method == 'POST':
        reviewer_id = request.POST.get('reviewer')
        if reviewer_id:
            reviewer = get_object_or_404(User, id=reviewer_id)
            # FIX: Review modelida 'status' yo'q — 'decision' ishlatiladi
            Review.objects.create(
                article=article,
                reviewer=reviewer,
                decision=Review.Decision.PENDING,  # Yangi taqriz — kutilmoqda
            )
            # FIX: Article.Status enum ishlatildi
            if article.status == Article.Status.DRAFT:
                article.status = Article.Status.REVIEW
                article.save(update_fields=['status'])

            messages.success(
                request,
                _("Taqrizchi {} muvaffaqiyatli tayinlandi.").format(
                    reviewer.get_full_name() or reviewer.username
                ),
            )
            return redirect('journal:editor_article_detail', pk=article.pk)

    context = {
        'article': article,
        'users': users,
    }
    return render(request, 'journal/dashboard/editor_assign_reviewer.html', context)


@user_passes_test(is_editor)
def editor_make_decision(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        rejection_reason = request.POST.get('rejection_reason', '').strip()

        if new_status and new_status in dict(Article.Status.choices):
            article.status = new_status
            # FIX: Rad etilganda sabab saqlanadi
            if new_status == Article.Status.REJECTED and rejection_reason:
                article.rejection_reason = rejection_reason
            article.save()
            messages.success(
                request,
                _("Maqola holati '{}'ga o'zgartirildi.").format(article.get_status_display())
            )
            return redirect('journal:editor_article_detail', pk=article.pk)

    context = {
        'article': article,
        'status_choices': Article.Status.choices,
    }
    return render(request, 'journal/dashboard/editor_make_decision.html', context)
