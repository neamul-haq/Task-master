from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from core.models import Role, UserRole
from users.models import UserProfile
from django.db import transaction
    
    
@receiver(user_logged_in)
def assign_role_on_first_login(sender, user, request, **kwargs):
    with transaction.atomic():
        if not hasattr(user, 'custom_role'):
            default_role, _ = Role.objects.get_or_create(name='User')
            UserRole.objects.create(user=user, role=default_role)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
        else:
            if hasattr(instance, 'userprofile'):
                instance.userprofile.save()


