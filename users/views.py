from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from users.forms import RegisterForm, CustomRegistrationForm, AssignRoleForm,CreateGroupForm, EditProfileForm
from django.contrib import messages
from users.forms import LoginForm, CustomPasswordChangeForm,CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from core.models import Role, UserRole
from django.views.generic.edit import UpdateView
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from decouple import config
from users.models import UserProfile    
from django.db import transaction
from urllib.parse import urlencode
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
from django.core.serializers.json import DjangoJSONEncoder
import re
from collections import defaultdict
from core.models import Permission, Role 

class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'
    
    def get_object(self):
        return self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['userprofile'] = UserProfile.objects.get(user=self.request.user)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['form'] = self.form_class(
            instance=self.object, userprofile = user_profile)
        return context
    def form_valid(self, form):
        with transaction.atomic():
            form.save(commit=True)
            self.request.user.refresh_from_db()  # 🔁 This ensures profile image is updated in memory
             # 🔍 DEBUG: Check if first_name was saved
            print("Memory first_name:", self.request.user.first_name)
            print("DB first_name:", User.objects.get(id=self.request.user.id).first_name)
        return redirect('profile')
    

#Test for users
# def is_admin(user):
#     return user.groups.filter(name='Admin').exists()

def is_admin(user):
    return hasattr(user, 'custom_role') and user.custom_role.role.name == 'Admin'


# Create your views here.
# def sign_up(request):
#     form = CustomRegistrationForm()#get
#     if request.method == 'POST':
#         form = CustomRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data.get('password1'))
#             user.is_active = False
#             user.save()
#             messages.success(
#                 request, 'A Confirmation mail sent. Please check your mail')
#             return redirect('sign-in')
#         else:
#             print("Form is not valid")
#     return render(request, 'registration/register.html', {"form" : form})

  # ✅ make sure these are imported

def sign_up(request):
    form = CustomRegistrationForm()
    
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()

            # ✅ Assign 'User' role after saving the user
            try:
                default_role = Role.objects.get(name='User')
                UserRole.objects.create(user=user, role=default_role)
            except Role.DoesNotExist:
                print("⚠️ Role 'User' not found. Make sure it's seeded.")
            
            messages.success(
                request, 'A Confirmation mail sent. Please check your mail'
            )
            return redirect('sign-in')
        else:
            print("Form is not valid")
    
    return render(request, 'registration/register.html', {"form": form})





def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html',{'form': form})


# @login_required
# def sign_out(request):
#     if request.method == 'POST':
#         logout(request)
#         return redirect('sign-in')
    

@login_required
def sign_out(request):
    django_logout(request)
    domain = config("APP_DOMAIN")
    client_id = config("APP_CLIENT_ID")
    return_to = request.build_absolute_uri('/')  # or your homepage
    params = {
        "client_id": client_id,
        "returnTo": return_to,
        "federated": ""  # empty string just includes the flag
    }

    return redirect(f"https://{domain}/v2/logout?" + urlencode(params))

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')
    except User.DoesNotExist:
        return HttpResponse('User not found')
       
@login_required
def vue_user_list(request):
    users = User.objects.all()
    users_data = [
        {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        } for user in users
    ]
    return render(request, 'admin/user_list.html', {
        'users_json': json.dumps(users_data, cls=DjangoJSONEncoder)
    })


@user_passes_test(is_admin, login_url='permission-denied')
def admin_dashboard(request):
    users = User.objects.select_related('custom_role__role').all()
    for user in users:
        user.role_name = user.custom_role.role.name if hasattr(user, 'custom_role') else 'No Role Assigned'

    users_data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role_name
        } for user in users
    ]

    return render(request, 'admin/dashboard.html', {
        "users_json": json.dumps(users_data, cls=DjangoJSONEncoder)
    })

        
        
@user_passes_test(is_admin, login_url='permission-denied')        
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')

            
            UserRole.objects.update_or_create(user=user, defaults={'role': role})

            messages.success(request, f"✅ User '{user.first_name} {user.last_name}' has been assigned the role: {role.name}")
            return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form, "user": user})


# @user_passes_test(is_admin, login_url='permission-denied')  
# def create_group(request):
#     form = CreateGroupForm()
    
#     if request.method == 'POST':
#         form = CreateGroupForm(request.POST)
#         if form.is_valid():
#             role = Role.objects.create(name=form.cleaned_data['name'])
#             permissions = form.cleaned_data['permissions']
#             role.permissions.set(permissions)

#             messages.success(request, f"✅ Role '{role.name}' created with {permissions.count()} permission(s).")
#             return redirect('create-group')
    
#     return render(request, 'admin/create_group.html', {'form': form})
def group_permissions():
    groups = defaultdict(list)
    for perm in Permission.objects.all():
        # Extract "task", "project", "task detail" from permission label
        match = re.search(r'Can \w+ (.+)', perm.label)
        if match:
            group = match.group(1).strip().title()  # normalize label
            groups[group].append(perm)
    return dict(groups)

def create_group(request):
    form = CreateGroupForm()
    grouped_permissions = group_permissions()

    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            role = Role.objects.create(name=form.cleaned_data['name'])
            permissions = form.cleaned_data['permissions']
            role.permissions.set(permissions)
            messages.success(request, f"✅ Role '{role.name}' created with {permissions.count()} permission(s).")
            return redirect('create-group')

    return render(request, 'admin/create_group.html', {
        'form': form,
        'grouped_permissions': grouped_permissions
    })



@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups':groups})


class CustomLoginView(LoginView):
    form_class = LoginForm
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()
    

class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    
    
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        user = self.request.user
        
        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['bio'] = user.userprofile.bio if hasattr(user, 'userprofile') else ''
        default_image = 'https://png.pngtree.com/png-clipart/20231019/original/pngtree-user-profile-avatar-png-image_13369988.png'
        profile = getattr(user, 'userprofile', None)
        context['profile_image'] = profile.profile_image.url if profile and profile.profile_image else default_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        
        return context
    
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')  
    html_email_template_name = 'registration/reset_email.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')  
    
    
    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset Successfully')
        return super().form_valid(form)
    

def redirect_to_reset_password(request):
    domain = config("APP_DOMAIN")
    client_id = config("APP_CLIENT_ID")
    reset_url = f"https://dev-h4kzavebg2vdwfhp.us.auth0.com/u/reset-password/index.html?client_id={client_id}"
    reset_url = f"https://{domain}/lo/reset?client_id={client_id}"
    return redirect(reset_url)



def user_list_view(request):
    users = list(User.objects.select_related('custom_role__role').values(
        'id', 'first_name', 'last_name', 'email', 'custom_role__role__name'
    ))
    for idx, user in enumerate(users, 1):
        user['number'] = idx
        user['custom_role'] = {'role': {'name': user.pop('custom_role__role__name')}}
    return render(request, 'admin/user_list.html', {
        'user_data': json.dumps(users, cls=DjangoJSONEncoder),
    })
