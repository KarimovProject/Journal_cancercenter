"""
Bu yordamchi sozlamalar fayli bo'lib, faqat SQLite'dan PostgreSQL'ga
avtomatik ma'lumotlarni ko'chirish vaqtida (dumpdata) ishlatiladi.
"""
from .base import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
