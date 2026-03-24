from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from events.models import Rsvp

@receiver(post_save, sender=Rsvp)
def send_rsvp_confirmation_email(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        event = instance.event
        
        # Email context
        context = {
            'username': user.username,
            'event_name': event.name,
            'date': event.date,
            'time': event.time,
            'location': event.location,
            'dashboard_url': f"{settings.FRONTEND_URL.rstrip('/')}{reverse('participant_dashboard')}"
        }

        # Render HTML version
        html_message = render_to_string('registration/rsvp_confirmation_email.html', context)

        try:
            send_mail(
                subject, 
                message, 
                settings.EMAIL_HOST_USER, 
                [user.email], 
                fail_silently=False,
                html_message=html_message
            )
        except Exception as e:
            print(f"Failed to send RSVP mail to {user.email}: {str(e)}")
