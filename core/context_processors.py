def user_role_context(request):
    role = None
    if request.user.is_authenticated and hasattr(request.user, 'custom_role'):
        role = request.user.custom_role.role
    return {'user_role': role}
