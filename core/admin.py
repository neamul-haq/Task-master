from django.contrib import admin

# Register your models here.
from core.models import Permission, Role, UserRole
# Register your models here.
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(UserRole)