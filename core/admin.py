from django.contrib import admin
from django.core.cache import cache
from django.contrib import messages
from core.models import Permission, Role, UserRole

# Register Permission model with default admin
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(UserRole)