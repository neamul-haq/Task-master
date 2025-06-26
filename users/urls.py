from django.urls import path, include
from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, assign_role,create_role, view_roles, edit_role
from users.views import CustomLoginView, ProfileView, ChangePassword, CustomPasswordResetView, CustomPasswordResetConfirmView, EditProfileView
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView
from users.views import redirect_to_reset_password, vue_user_list
# from django.views.generic import TemplateView

urlpatterns = [
    path('', include('social_django.urls')),  # This enables /complete/auth0 etc.
    path('sign-out/', sign_out, name='logout'),

    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/create-role/', create_role, name='create-role'),
    path('admin/view-roles/',view_roles , name='view-roles'),
    path('admin/edit-role/<int:role_id>/', edit_role, name='edit-role'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('password-change/', ChangePassword.as_view(), name='password-change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),#ekhane name ta same etai dite hobe
    path('password-reset/', CustomPasswordResetView.as_view(), name='password-reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),#name ta same etai dite hobe
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path("reset-password-auth0/", redirect_to_reset_password, name="reset-password-auth0"),
    path('users_list/', vue_user_list, name='user-list'),

]