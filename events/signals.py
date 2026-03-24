import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Rsvp
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.utils import email_sender

@receiver(post_save, sender=Rsvp)
def send_rsvp_confirmation_email(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        event = instance.event
        subject = f"RSVP Confirmation for {event.name}"
        
        context = {
            'user': user,
            'event': event,
        }
        html_message = render_to_string('registration/rsvp_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email in a background thread to prevent blocking the RSVP process
        thread = threading.Thread(
            target=email_sender,
            args=(subject, plain_message, settings.EMAIL_HOST_USER, [user.email], html_message)
        )
        thread.start()
