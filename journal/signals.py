from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Article


@receiver(post_save, sender=Article)
def notify_author_on_status_change(sender, instance, created, **kwargs):
    """Send email to author when article status changes to published or rejected."""
    if created or not instance.submitted_by:
        return

    # Skip if this is not a status change (compare with DB value)
    try:
        old = Article.objects.get(pk=instance.pk)
    except Article.DoesNotExist:
        return
    # post_save fires after save, so instance IS the current state.
    # We need to detect if status changed — use _state to check if it's an update
    if kwargs.get('raw'):
        return

    user = instance.submitted_by
    if not user.email:
        return

    site_name = getattr(settings, 'SITE_NAME', 'Oncoscience')
    site_domain = getattr(settings, 'SITE_DOMAIN', 'http://localhost:8000')

    if instance.status == Article.Status.PUBLISHED:
        subject = f'[{site_name}] Maqolangiz chop etildi'
        message = (
            f'Hurmatli {user.get_full_name() or user.username},\n\n'
            f'"{instance.title}" sarlavhali maqolangiz chop etildi.\n'
            f'Maqolani ko\'rish: {site_domain}/ilm-fan/maqolalar/{instance.slug}/\n\n'
            f'{site_name} tahririyati'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

    elif instance.status == Article.Status.REJECTED:
        reason = instance.rejection_reason or _('Sabab ko\'rsatilmagan.')
        subject = f'[{site_name}] Maqolangiz ko\'rib chiqildi'
        message = (
            f'Hurmatli {user.get_full_name() or user.username},\n\n'
            f'"{instance.title}" sarlavhali maqolangiz ko\'rib chiqildi.\n'
            f'Holat: Rad etilgan\n'
            f'Sabab: {reason}\n\n'
            f'Maqolani tahrir qilib qayta topshirishingiz mumkin.\n'
            f'{site_domain}/ilm-fan/mening-maqolalarim/\n\n'
            f'{site_name} tahririyati'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
