from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from events.models import Rsvp

@receiver(post_save, sender=Rsvp)
def send_rsvp_confirmation_email(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        event = instance.event
        subject = f"RSVP Confirmation for {event.name}"
        message = (
            f"Hi {user.username},\n\n"
            f"You have successfully RSVP'd for the event: {event.name}\n"
            f"Date: {event.date}\n"
            f"Time: {event.time}\n"
            f"Location: {event.location}\n\n"
            f"Thank you for your participation!"
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
