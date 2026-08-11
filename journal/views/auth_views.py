"""
journal/views/auth_views.py

Autentifikatsiya: ro'yxatdan o'tish, kirish, chiqish, newsletter.
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from ipware import get_client_ip

from ..forms import RegistrationForm
from ..models import NewsletterSubscription


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


def register_view(request):
    if request.user.is_authenticated:
        return redirect('journal:home')
    if request.method == 'POST':
        if _rate_limited(request, 'register', limit=10, window=3600):
            messages.error(request, _('Juda koʻp urinish. Iltimos, birozdan soʻng qayta urining.'))
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


@require_POST
def newsletter_subscribe(request):
    """'Sign up for alerts' — double opt-in orqali email tasdiqlash."""
    email = (request.POST.get('email') or '').strip().lower()
    next_url = request.POST.get('next') or reverse('journal:home')

    if _rate_limited(request, 'newsletter', limit=5, window=3600):
        messages.error(request, _("Juda koʻp urinish. Iltimos, birozdan soʻng qayta urining."))
        return redirect(next_url)

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, _("Iltimos, toʻgʻri email manzil kiriting."))
        return redirect(next_url)

    obj, created = NewsletterSubscription.objects.get_or_create(email=email)
    if obj.is_confirmed:
        messages.info(request, _('Bu email allaqachon obuna boʻlgan.'))
        return redirect(next_url)

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
            f'{site_name} yangiliklariga obuna boʻlish uchun quyidagi havolani bosing:\n'
            f'{confirm_url}\n\n'
            f'Agar bu siz boʻlmasangiz, ushbu xatni eʼtiborsiz qoldiring.'
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
        messages.error(request, _("Tasdiqlash havolasi yaroqsiz yoki muddati oʻtgan."))
        return redirect('journal:home')
    obj.is_confirmed = True
    obj.is_active = True
    obj.confirm_token = ''
    obj.save(update_fields=['is_confirmed', 'is_active', 'confirm_token'])
    messages.success(request, _('Obunangiz tasdiqlandi! Yangi maqolalar haqida xabar beramiz.'))
    return redirect('journal:home')
