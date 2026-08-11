"""
journal/views/submission.py

Maqola yuborish, tahrirlash, mening maqolalarim, profil.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from ..forms import (
    ArticleFigureFormSet,
    ArticleSubmissionForm,
    ArticleSupplementaryFileFormSet,
    AuthorProfileForm,
    ReferenceFormSet,
)
from ..models import Article, Author


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

    initial = {}
    if article.keywords.exists():
        initial['keywords_text'] = ', '.join(k.name for k in article.keywords.all())
    if article.issue:
        initial['issue_text'] = f'Vol. {article.issue.volume}, No. {article.issue.number}, {article.issue.year}'
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

            messages.success(request, _("Maqola yangilandi va qayta koʻrib chiqishga yuborildi."))
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
    articles = (
        Article.objects
        .filter(submitted_by=request.user)
        .select_related('category', 'issue')
        .prefetch_related('authors')
        .order_by('-created_at')
    )
    agg = articles.aggregate(
        total_views=Sum('views_count'),
        total_citations=Sum('citation_count'),
    )
    stats = {
        'total': articles.count(),
        'published': articles.filter(status=Article.Status.PUBLISHED).count(),
        'draft': articles.filter(status=Article.Status.DRAFT).count(),
        'review': articles.filter(status=Article.Status.REVIEW).count(),
        'rejected': articles.filter(status=Article.Status.REJECTED).count(),
        'total_views': agg['total_views'] or 0,
        'total_citations': agg['total_citations'] or 0,
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
        author = Author.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
        )

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
