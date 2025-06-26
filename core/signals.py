from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Role, UserRole 

@receiver(m2m_changed, sender=Role.permissions.through)
def clear_role_permissions_cache(sender, instance, action, **kwargs):
    """
    Clears cache for all users associated with a role when its permissions change.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        # 'instance' here is the Role object whose permissions were changed.
        users_with_role = UserRole.objects.filter(role=instance).values_list('user__id', flat=True)
        for user_id in users_with_role:
            # For each user that has this role, clear their specific permission caches
            cache.delete_pattern(f"user:{user_id}:permission:*")
            print(f"🗑️ Cleared cache for user {user_id}'s permissions due to role '{instance.name}' permission change.")