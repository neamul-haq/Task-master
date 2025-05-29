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

# @receiver(post_save, sender=User)
# def send_activation_email(sender, instance, created, **kwargs):
#     if created:
#         sender.is_active = False  # Deactivate the user by default
#         sender.save()
#         token = default_token_generator.make_token(instance)
#         activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"
        
#         subject = 'Activate Your Account'
#         message = f'Hi {instance.username}, \n\nPlease activate your account by clicking the link below:\n{
#             activation_url}\n\nThank You!'
#         recipient_list = [instance.email]
        
#         try:
#             send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
#         except Exception as e:
#             print(f"Failed to send email to {instance.email}: {str(e)}")
            
            
# @receiver(post_save, sender=User)
# def assign_role(sender, instance, created, **kwargs):
#     if created:
#         user_group, created = Group.objects.get_or_create(name='User')
#         instance.groups.add(user_group)
#         instance.save()



#this is not work for auth0 user
# @receiver(post_save, sender=User)
# def assign_role(sender, instance, created, **kwargs):
#     if created:
#         # Get or create default "User" role
#         default_role, _ = Role.objects.get_or_create(name='User')

#         # Assign role to the new user
#         UserRole.objects.create(user=instance, role=default_role)
    
    
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
            # Ensure profile exists before saving
            if hasattr(instance, 'userprofile'):
                instance.userprofile.save()


