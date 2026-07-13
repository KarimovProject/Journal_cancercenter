from django.conf import settings

from .models import JournalInfo


def site_settings(request):
    """Expose common site-level values to every template."""
    try:
        journal_info = JournalInfo.load()
    except Exception:
        # Migratsiyalardan oldin yoki jadval bo'lmasa xatolik bermasin.
        journal_info = None
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Oncoscience'),
        'SITE_DOMAIN': getattr(settings, 'SITE_DOMAIN', ''),
        'LANGUAGES': settings.LANGUAGES,
        'journal_info': journal_info,
    }
