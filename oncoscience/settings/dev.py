"""
oncoscience/settings/dev.py

Local development sozlamalari.
Ishlatish: DJANGO_SETTINGS_MODULE=oncoscience.settings.dev
"""
import os

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-chaz#r&ik^pt&pla1+9%lt-e6!($#x2qgphgu*i834t2x%=@6s')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
] + [
    f'http://{h}:{p}' for h in ('localhost', '127.0.0.1')
    for p in range(5000, 5200)
]

# Database — local SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Email — console da ko'rsatiladi (smtp yuborilmaydi)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS — dev da barcha manbalarga ruxsat
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (o'rnatilgan bo'lsa)
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']  # noqa: F405
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # noqa: F405
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
