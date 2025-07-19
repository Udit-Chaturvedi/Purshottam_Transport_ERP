from celery import shared_task
from django.core.mail import send_mail
from .models import User
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_password_reset_email(email, otp_code):
    try:
        subject = 'Password Reset OTP'
        message = f"Your OTP code is {otp_code}. It expires in 10 minutes."
        send_mail(subject, message, 'no-reply@purshottamtransport.com', [email])
        logger.info(f"Sent OTP to {email}")
    except Exception as e:
        logger.error(f"Error sending OTP to {email}: {e}")
