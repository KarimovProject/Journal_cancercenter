from journal.models import Notification
Notification.objects.filter(link__contains='SITE_DOMAIN=').update(link='/ilm-fan/taqriz-paneli/')
