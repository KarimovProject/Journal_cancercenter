import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from .tasks import send_email_task, watermark_pdf_task
from django.utils.translation import gettext_lazy as _

from .models import Article, Review

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Article)
def send_article_status_email(sender, instance, created, **kwargs):
    if created:
        return
        
    # We can detect status change if we store original status, but for simplicity
    # we'll send email when it becomes published or goes under review
    # Ideally, we should check what changed using a mixin, but let's just do a basic one.
    if instance.status == Article.Status.PUBLISHED:
        # Trigger watermarking
        watermark_pdf_task.delay(instance.id)
        
        subject = f"Maqolangiz nashr etildi: {instance.title_uz}"
        url = f"{settings.SITE_DOMAIN}{instance.get_absolute_url()}"
        message = f"Hurmatli muallif,\n\nSizning '{instance.title_uz}' nomli maqolangiz Oncoscience jurnalida nashr etildi.\n\nMaqolani ko'rish uchun havola: {url}"
    elif instance.status == Article.Status.REVIEW:
        subject = f"Maqolangiz taqrizga yuborildi: {instance.title_uz}"
        message = f"Hurmatli muallif,\n\nSizning '{instance.title_uz}' nomli maqolangiz taqriz jarayoniga o'tkazildi. Natijalar haqida qo'shimcha xabar beramiz."
    elif instance.status == Article.Status.REJECTED:
        subject = f"Maqolangiz rad etildi: {instance.title_uz}"
        message = f"Hurmatli muallif,\n\nSizning '{instance.title_uz}' nomli maqolangiz afsuski qabul qilinmadi.\nSabab: {instance.rejection_reason}"
    else:
        return

    author = instance.submitted_by
    if author and author.email:
        try:
            send_email_task.delay(
                subject,
                message,
                [author.email]
            )
        except Exception as e:
            logger.error(f"Failed to send email to {author.email}: {e}")

@receiver(post_save, sender=Review)
def send_review_emails(sender, instance, created, **kwargs):
    if created:
        # Taqrizchiga maqola biriktirilganda xat yuborish
        subject = f"Sizga taqriz uchun maqola biriktirildi"
        site_domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
        url = f"{site_domain}{reverse('journal:reviewer_dashboard')}"
        message = f"Hurmatli {instance.reviewer.get_full_name() or instance.reviewer.username},\n\nSizga '{instance.article.title_uz}' nomli maqola taqriz uchun biriktirildi.\nIltimos, saytga kirib 'Taqrizchi Paneli' orqali maqola bilan tanishing va o'z xulosangizni yuboring.\n\nHavola: {url}"
        
        if instance.reviewer.email:
            try:
                send_email_task.delay(
                    subject,
                    message,
                    [instance.reviewer.email]
                )
            except Exception as e:
                logger.error(f"Failed to send assignment email: {e}")
                
    elif instance.decision != Review.Decision.PENDING:
        # Taqrizchi xulosasini saqlaganda muharrirga xat yuborish
        subject = f"Taqriz yakunlandi: {instance.article.title_uz}"
        message = f"Yangi taqriz xulosasi: {instance.get_decision_display()}.\nMaqola: {instance.article.title_uz}\n\nFikr-mulohazalar: {instance.comments_for_editor}"
        
        try:
            send_email_task.delay(
                subject,
                message,
                [settings.DEFAULT_FROM_EMAIL]
            )
        except Exception as e:
            logger.error(f"Failed to send review email: {e}")
