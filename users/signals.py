from django.dispatch import receiver
from django.db.models.signals import post_save,pre_delete,pre_save,post_delete,m2m_changed
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

@receiver(post_save, sender = User)
def send_activation_email (sender, instance, created, **kwargs):
    if created :
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}"
        subject = "Active Your Account "
        message = f"Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_url}\n\n""Thank you!"

        recipient_list = [instance.email]

        try:
            
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
        except Exception as e :
            print(f"Failed to send mail {instance.email}: {str(e)}")




@receiver(post_save, sender= User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        participant_group, created = Group.objects.get_or_create(name='Participant')
        instance.groups.add(participant_group)
        instance.save()