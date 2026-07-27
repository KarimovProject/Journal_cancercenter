from journal.models import Notification
notifs = Notification.objects.all()
for n in notifs:
    n.link = '/ilm-fan/taqriz-paneli/'
    n.save()
    print('UPDATED:', n.id)
