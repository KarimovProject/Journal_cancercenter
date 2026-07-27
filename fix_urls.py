from journal.models import Notification
Notification.objects.filter(link__contains='taqriz-paneli').update(link='/ilm-fan/taqriz-paneli/')
print(" Fixed notifications.\)
