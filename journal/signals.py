import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from .tasks import send_email_task, watermark_pdf_task
from django.utils.translation import gettext_lazy as _

from .models import Article, Review, Notification, NewsletterSubscription

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def send_article_status_email(sender, instance, created, **kwargs):
    if created:
        return

    subject = None
    message = None
    notification_link = ''

    if instance.status == Article.Status.PUBLISHED:
        # Watermarking vazifasini ishga tushirish
        watermark_pdf_task.delay(instance.id)

        article_url = f"{settings.SITE_DOMAIN}{instance.get_absolute_url()}"
        notification_link = article_url

        subject = f"Maqolangiz nashr etildi: {instance.title_uz}"
        message = (
            f"Hurmatli muallif,\n\n"
            f"Sizning '{instance.title_uz}' nomli maqolangiz Oncoscience jurnalida nashr etildi.\n\n"
            f"Maqolani ko'rish uchun havola: {article_url}"
        )

        # Obunachilarga (Subscribers) xabar yuborish
        subscriber_subject = f"Yangi maqola nashr etildi: {instance.title_uz}"
        subscriber_message = (
            f"Hurmatli obunachi,\n\n"
            f"Oncoscience jurnalida yangi maqola nashr etildi:\n\n"
            f"{instance.title_uz}\n\n"
            f"O'qish uchun havola: {article_url}\n\n"
            f"Ushbu xabar sizning obunangiz asosida yuborilmoqda."
        )
        subscribers = NewsletterSubscription.objects.filter(is_active=True, is_confirmed=True)
        for sub in subscribers:
            try:
                send_email_task.delay(subscriber_subject, subscriber_message, [sub.email])
            except Exception as e:
                logger.error(f"Failed to send newsletter email to {sub.email}: {e}")

    elif instance.status == Article.Status.REVIEW:
        # FIX: notification_link va subject/message aniqlanadi
        dashboard_url = f"{settings.SITE_DOMAIN}/ilm-fan/mening-maqolalarim/"
        notification_link = dashboard_url

        subject = f"Maqolangiz taqrizga yuborildi: {instance.title_uz}"
        message = (
            f"Hurmatli muallif,\n\n"
            f"Sizning '{instance.title_uz}' nomli maqolangiz taqriz jarayoniga o'tkazildi.\n"
            f"Natijalar haqida qo'shimcha xabar beramiz.\n\n"
            f"Maqolalaringiz: {dashboard_url}"
        )

    elif instance.status == Article.Status.REJECTED:
        # FIX: notification_link va to'liq ma'lumot
        dashboard_url = f"{settings.SITE_DOMAIN}/ilm-fan/mening-maqolalarim/"
        notification_link = dashboard_url

        rejection_reason = getattr(instance, 'rejection_reason', '') or _('Sabab ko\'rsatilmagan.')
        subject = f"Maqolangiz rad etildi: {instance.title_uz}"
        message = (
            f"Hurmatli muallif,\n\n"
            f"Sizning '{instance.title_uz}' nomli maqolangiz afsuski qabul qilinmadi.\n"
            f"Sabab: {rejection_reason}\n\n"
            f"Maqolani qayta ishlash uchun: {dashboard_url}"
        )

    # subject aniqlanmagan bo'lsa — bu holat bizni qiziqtirmaydi
    if not subject:
        return

    author = instance.submitted_by
    if not author:
        return

    # In-App Notification yaratish
    Notification.objects.create(
        user=author,
        message=subject,
        link=notification_link,
    )

    # Email yuborish
    if author.email:
        try:
            send_email_task.delay(subject, message, [author.email])
        except Exception as e:
            logger.error(f"Failed to send email to {author.email}: {e}")


@receiver(post_save, sender=Review)
def send_review_emails(sender, instance, created, **kwargs):
    site_domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')

    if created:
        # Taqrizchiga maqola biriktirilganda xat yuborish
        dashboard_url = f"{site_domain}{reverse('journal:reviewer_dashboard')}"
        subject = "Sizga taqriz uchun maqola biriktirildi"
        message = (
            f"Hurmatli {instance.reviewer.get_full_name() or instance.reviewer.username},\n\n"
            f"Sizga '{instance.article.title_uz}' nomli maqola taqriz uchun biriktirildi.\n"
            f"Iltimos, saytga kirib 'Taqrizchi Paneli' orqali maqola bilan tanishing.\n\n"
            f"Havola: {dashboard_url}"
        )

        if instance.reviewer:
            Notification.objects.create(
                user=instance.reviewer,
                message=subject,
                link=dashboard_url,
            )
            if instance.reviewer.email:
                try:
                    send_email_task.delay(subject, message, [instance.reviewer.email])
                except Exception as e:
                    logger.error(f"Failed to send assignment email: {e}")

    elif instance.decision != Review.Decision.PENDING:
        # Taqrizchi xulosasini saqlaganda muharrirga xat yuborish
        subject = f"Taqriz yakunlandi: {instance.article.title_uz}"
        message = (
            f"Yangi taqriz xulosasi: {instance.get_decision_display()}.\n"
            f"Maqola: {instance.article.title_uz}\n\n"
            f"Muallif uchun fikr-mulohazalar: {instance.comments_for_author}\n"
            f"Muharrir uchun: {instance.comments_for_editor}"
        )
        try:
            send_email_task.delay(subject, message, [settings.DEFAULT_FROM_EMAIL])
        except Exception as e:
            logger.error(f"Failed to send review email: {e}")
