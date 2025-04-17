from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from users.forms import RegisterForm, CustomRegistrationForm, AssignRoleForm,CreateGroupForm
from django.contrib import messages
from users.forms import LoginForm, CustomPasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from tasks.models import Task
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views.generic import TemplateView

#Test for users
def is_admin(user):
    return user.groups.filter(name='Admin').exists()
# Create your views here.
def sign_up(request):
    form = CustomRegistrationForm()#get
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(
                request, 'A Confirmation mail sent. Please check your mail')
            return redirect('sign-in')
        else:
            print("Form is not valid")
    return render(request, 'registration/register.html', {"form" : form})


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


@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')
    
    
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
    
    

    
@user_passes_test(is_admin, login_url='no-permission')  
def admin_dashboard(request):
    users = User.objects.prefetch_related('groups').all()
    
    for user in users:
        if user.groups.exists():
            user.group_name = user.groups.first().name
        else:
            user.group_name = 'No Group Assigned'
    return render(request, 'admin/dashboard.html', {"users":users})

@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()
    
    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear() #Remove old roles
            user.groups.add(role)
            messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
            return redirect('admin-dashboard')
        
    return render(request, 'admin/assign_role.html', {"form" : form})
        
@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')
        
    return render(request, 'admin/create_group.html', {'form': form})

@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups':groups})

@user_passes_test(is_admin, login_url='no-permission')
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
        
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        
        return context