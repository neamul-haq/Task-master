
from django.db import models
from django.contrib.auth.models import User

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

    objects = UserRoleManager()  #  Attaching the custom manager here

    def __str__(self):
        return f"{self.user.username} → {self.role.name}"
