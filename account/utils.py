import random
from django.core.mail import send_mail
from django.conf import settings


def generate_code():
    return str(random.randint(100000, 999999))


def send_registration_code(email, code):
    send_mail(
        subject="Подтверждение регистрации",
        message=f"Ваш код подтверждения регистрации: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def send_password_reset_code(email, code):
    send_mail(
        subject="Подтверждение смены пароля",
        message=f"Ваш код для смены пароля: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
def send_email_change_code(email, code):
    send_mail(
        subject="Подтверждение email",
        message=f"Ваш код для email: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )