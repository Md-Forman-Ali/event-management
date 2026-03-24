from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group

def email_sender(subject, plain_message, from_email, recipient_list, html_message):
    try:
        if not from_email:
            print("CRITICAL: EMAIL_HOST_USER is NOT SET. Check environment variables.")
            return

        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        print(f"Email sent successfully to {recipient_list}")
    except Exception as e:
        print(f"CRITICAL: Failed to send mail: {str(e)}")
        print(f"SMTP Settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}")

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Admin').exists())

def is_organizer(user):
    return user.is_authenticated and user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.is_authenticated and user.groups.filter(name='Participant').exists()

def get_user_role(user):
    if not user.is_authenticated:
        return None
    if is_admin(user):
        return 'Admin'
    if is_organizer(user):
        return 'Organizer'
    if is_participant(user):
        return 'Participant'
    return None
