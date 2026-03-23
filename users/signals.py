import threading
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()

def email_sender(subject, plain_message, from_email, recipient_list, html_message):
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
    except Exception as e:
        print(f"Failed to send mail: {str(e)}")

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        # Use settings.FRONTEND_URL which is now dynamic
        activation_url = f"{settings.FRONTEND_URL}users/activate/{instance.id}/{token}"
        subject = "Activate Your Account - EventMaster"
        
        context = {
            'user': instance,
            'activation_url': activation_url,
        }
        html_message = render_to_string('registration/activation_email.html', context)
        plain_message = strip_tags(html_message)

        # Send email in a separate thread to prevent blocking the request
        thread = threading.Thread(
            target=email_sender,
            args=(subject, plain_message, settings.EMAIL_HOST_USER, [instance.email], html_message)
        )
        thread.start()

@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        participant_group, _ = Group.objects.get_or_create(name='Participant')
        instance.groups.add(participant_group)
        # Note: instance.save() is not needed here as groups.add() persists the relationship
        # and avoids redundant post_save signal triggers.