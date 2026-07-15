from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Article


@receiver(pre_save, sender=Article)
def _remember_old_status(sender, instance, **kwargs):
    """Capture the previous status before the save so post_save can compare."""
    if not instance.pk:
        instance._old_status = None
        return
    try:
        instance._old_status = (
            Article.objects.filter(pk=instance.pk)
            .values_list('status', flat=True)
            .first()
        )
    except Article.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Article)
def notify_author_on_status_change(sender, instance, created, **kwargs):
    """Email the submitting author when the article status actually changes."""
    if created or kwargs.get('raw'):
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return

    user = instance.submitted_by
    if not user or not user.email:
        return

    site_name = getattr(settings, 'SITE_NAME', 'Oncoscience')
    site_domain = getattr(settings, 'SITE_DOMAIN', 'http://localhost:8000')
    greeting = user.get_full_name() or user.username
    article_url = f'{site_domain}/ilm-fan/maqolalar/{instance.slug}/'
    my_url = f'{site_domain}/ilm-fan/mening-maqolalarim/'

    subject = message = None

    if instance.status == Article.Status.REVIEW:
        subject = f'[{site_name}] Maqolangiz ko\'rib chiqilmoqda'
        message = (
            f'Hurmatli {greeting},\n\n'
            f'"{instance.title}" sarlavhali maqolangiz tahririyat tomonidan '
            f'ko\'rib chiqishga qabul qilindi.\n'
            f'Natija haqida qo\'shimcha xabar beramiz.\n\n'
            f'{my_url}\n\n{site_name} tahririyati'
        )
    elif instance.status == Article.Status.PUBLISHED:
        subject = f'[{site_name}] Maqolangiz chop etildi'
        message = (
            f'Hurmatli {greeting},\n\n'
            f'"{instance.title}" sarlavhali maqolangiz chop etildi.\n'
            f'Maqolani ko\'rish: {article_url}\n\n'
            f'{site_name} tahririyati'
        )
    elif instance.status == Article.Status.REJECTED:
        reason = instance.rejection_reason or 'Sabab ko\'rsatilmagan.'
        subject = f'[{site_name}] Maqolangiz ko\'rib chiqildi'
        message = (
            f'Hurmatli {greeting},\n\n'
            f'"{instance.title}" sarlavhali maqolangiz ko\'rib chiqildi.\n'
            f'Holat: Rad etilgan\nSabab: {reason}\n\n'
            f'Maqolani tahrir qilib qayta topshirishingiz mumkin.\n'
            f'{my_url}\n\n{site_name} tahririyati'
        )

    if subject and message:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
