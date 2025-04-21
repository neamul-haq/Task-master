from django.db import models
from django.contrib.auth.models import User

class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=150)

    def __str__(self):
        return self.label


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, related_name='roles')

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_role')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username} → {self.role.name}"
