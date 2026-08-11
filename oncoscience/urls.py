"""
URL configuration for oncoscience project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import RedirectView

from journal.feeds import LatestArticlesFeed
from journal.sitemaps import sitemaps


def robots_txt(request):
    lines = [
        'User-agent: *',
        f"Disallow: /{os.getenv('ADMIN_URL_PATH', 'boshqaruv-markazi/')}",
        'Disallow: /ilm-fan/mening-maqolalarim/',
        'Disallow: /ilm-fan/profil/',
        'Disallow: /ilm-fan/maqola-yuborish/',
        '',
        f'Sitemap: {settings.SITE_DOMAIN}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


urlpatterns = [
    path('', RedirectView.as_view(url='/ilm-fan/', permanent=False)),
    path('debug-migration/', views.debug_migration_log),
    path(os.getenv('ADMIN_URL_PATH', 'boshqaruv-markazi/'), admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('journal.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('rss/', LatestArticlesFeed(), name='rss_feed'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('ilm-fan/', include('journal.urls')),
]

handler404 = 'journal.views.custom_404'
handler500 = 'journal.views.custom_500'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Serve media files in production as well, since there is no Nginx serving them
from django.urls import re_path
from django.views.static import serve
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
