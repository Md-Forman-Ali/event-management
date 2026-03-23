from django.dispatch import receiver
from django.db.models.signals import post_save,pre_delete,pre_save,post_delete,m2m_changed
from django.contrib.auth.models import  Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()

from django.template.loader import render_to_string
from django.utils.html import strip_tags

@receiver(post_save, sender = User)
def send_activation_email (sender, instance, created, **kwargs):
    if created :
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}users/activate/{instance.id}/{token}"
        subject = "Activate Your Account - EventMaster"
        
        context = {
            'user': instance,
            'activation_url': activation_url,
        }
        html_message = render_to_string('registration/activation_email.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [instance.email], html_message=html_message, fail_silently=False)
        except Exception as e :
            print(f"Failed to send mail {instance.email}: {str(e)}")




@receiver(post_save, sender= User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        participant_group, created = Group.objects.get_or_create(name='Participant')
        instance.groups.add(participant_group)
        instance.save()