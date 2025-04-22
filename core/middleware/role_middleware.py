from django.shortcuts import redirect
from django.urls import reverse
from core.models import UserRole

class RoleAccessControlMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        if request.path == reverse('permission-denied'):
            return None

        # ✅ Detect permission from function-based OR class-based views
        permission_required = getattr(view_func, 'required_permission', None)

        # 🧠 Handle CBVs: check the view class instead
        if not permission_required and hasattr(view_func, 'view_class'):
            permission_required = getattr(view_func.view_class, 'required_permission', None)

        if not permission_required:
            return None  # 🔓 No permission needed for this view

        try:
            role = request.user.custom_role.role
        except UserRole.DoesNotExist:
            return redirect(reverse('permission-denied'))

        if role.permissions.filter(code=permission_required).exists():
            return None  # ✅ allowed

        print(f"❌ Access denied for {request.user.username} to {permission_required}")
        return redirect(reverse('permission-denied'))
