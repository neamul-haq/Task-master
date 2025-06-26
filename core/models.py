from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache 



class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=150)

    def __str__(self):
        return self.code
    

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, related_name='roles')

    def __str__(self):
        return self.name


class UserRoleManager(models.Manager):
    def get_role_name(self, user):
        if hasattr(user, 'custom_role') and user.custom_role:
            return user.custom_role.role.name
        return None

    def has_permission(self, user, permission_code):
        if not user.is_authenticated:
            return False
        if not hasattr(user, 'custom_role'):
            return False
        return user.custom_role.role.permissions.filter(code=permission_code).exists()


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_role')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')

    objects = UserRoleManager()

    def __str__(self):
        return f"{self.user.username} → {self.role.name}"

    # Add this method to clear cache on save
    def save(self, *args, **kwargs):
        # Clear cache for this user's permissions before saving the new role
        self.clear_user_permissions_cache()
        super().save(*args, **kwargs)

    # Add this method to clear cache on delete
    def delete(self, *args, **kwargs):
        # Clear cache for this user's permissions before deleting the role
        self.clear_user_permissions_cache()
        super().delete(*args, **kwargs)

    def clear_user_permissions_cache(self):
        # We need to clear all permission-related cache entries for this user
        # Since we don't know which specific permissions were cached,
        # it's safest to delete all keys matching the user's pattern.
        # Alternatively, if you only cache a few specific permissions,
        # you could explicitly delete those keys.

        # Note: django-redis provides delete_pattern, which is very useful here.
        cache.delete_pattern(f"user:{self.user.id}:permission:*")
        print(f"🗑️ Cleared cache for user {self.user.username}'s permissions.")