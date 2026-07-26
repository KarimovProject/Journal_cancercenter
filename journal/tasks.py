import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import os

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=True,
        )
        logger.info(f"Email sent to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}")

@shared_task
def watermark_pdf_task(article_id):
    try:
        from journal.models import Article
        from PyPDF2 import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import io
        
        article = Article.objects.get(id=article_id)
        if not article.pdf_file:
            return
            
        original_pdf_path = article.pdf_file.path
        if not os.path.exists(original_pdf_path):
            return
            
        # Create watermark
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont("Helvetica-Bold", 12)
        can.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.5)
        text = f"Oncoscience Journal - Vol. {article.issue.volume if article.issue else ''} {article.issue.year if article.issue else ''}"
        can.drawString(50, 30, text)
        can.save()
        packet.seek(0)
        
        watermark = PdfReader(packet)
        watermark_page = watermark.pages[0]
        
        pdf = PdfReader(original_pdf_path)
        writer = PdfWriter()
        
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            page.merge_page(watermark_page)
            writer.add_page(page)
            
        with open(original_pdf_path, "wb") as outputStream:
            writer.write(outputStream)
            
        logger.info(f"Watermarked PDF for article {article_id}")
        
    except Exception as e:
        logger.error(f"Error watermarking PDF for article {article_id}: {e}")
