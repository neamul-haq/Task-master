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
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
        
    #     user = authenticate(request, username=username, password=password)
        
    #     if user is not None:
    #         login(request, user)
    #         return redirect('home')
    # return render(request, 'registration/login.html')
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
    return HttpResponseRedirect(
        f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}&federated"
    )

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
       

    
# @user_passes_test(is_admin, login_url='no-permission')  
# def admin_dashboard(request):
#     users = User.objects.prefetch_related('groups').all()
    
#     for user in users:
#         if user.groups.exists():
#             user.group_name = user.groups.first().name
#         else:
#             user.group_name = 'No Group Assigned'
#     return render(request, 'admin/dashboard.html', {"users":users})

@user_passes_test(is_admin, login_url='permission-denied')  # ✅ custom permission page
def admin_dashboard(request):
    users = User.objects.select_related('custom_role__role').all()

    for user in users:
        if hasattr(user, 'custom_role'):
            user.role_name = user.custom_role.role.name
        else:
            user.role_name = 'No Role Assigned'

    return render(request, 'admin/dashboard.html', {"users": users})


# @user_passes_test(is_admin, login_url='permission-denied')
# def assign_role(request, user_id):
#     user = User.objects.get(id=user_id)
#     form = AssignRoleForm()
    
#     if request.method == 'POST':
#         form = AssignRoleForm(request.POST)
#         if form.is_valid():
#             role = form.cleaned_data.get('role')
#             user.groups.clear() #Remove old roles
#             user.groups.add(role)
#             messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
#             return redirect('admin-dashboard')
        
#     return render(request, 'admin/assign_role.html', {"form" : form})
        
        
@user_passes_test(is_admin, login_url='permission-denied')        
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')

            
            UserRole.objects.update_or_create(user=user, defaults={'role': role})

            messages.success(request, f"✅ User '{user.username}' has been assigned the role: {role.name}")
            return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form, "user": user})

        
# @user_passes_test(is_admin, login_url='no-permission')
# def create_group(request):
#     form = CreateGroupForm()
#     if request.method == 'POST':
#         form = CreateGroupForm(request.POST)
        
#         if form.is_valid():
#             group = form.save()
#             messages.success(request, f"Group {group.name} has been created successfully")
#             return redirect('create-group')
        
#     return render(request, 'admin/create_group.html', {'form': form})


@user_passes_test(is_admin, login_url='permission-denied')  
def create_group(request):
    form = CreateGroupForm()
    
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            role = Role.objects.create(name=form.cleaned_data['name'])
            permissions = form.cleaned_data['permissions']
            role.permissions.set(permissions)

            messages.success(request, f"✅ Role '{role.name}' created with {permissions.count()} permission(s).")
            return redirect('create-group')
    
    return render(request, 'admin/create_group.html', {'form': form})



@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups':groups})

@user_passes_test(is_admin, login_url='permission-denied')
def view_task(request):
    #Retrieve all data from Task Model
    tasks = Task.objects.all()
    return render(request, "admin/show_tasks.html", {"tasks": tasks})

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