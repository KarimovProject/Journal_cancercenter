
import os
import django
from journal.models import Notification

for n in Notification.objects.all():
    n.link = '/ilm-fan/taqriz-paneli/'
    n.save()
    print('UPDATED:', n.id)
