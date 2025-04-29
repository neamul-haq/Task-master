# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
# from tasks.models import Task, TaskDetail, Project
# from django.db.models import Q, Count, Avg, Min, Max
# from django.contrib import messages
# from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
# from datetime import date
# from django.views import View
# from django.utils.decorators import method_decorator
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# from django.views.generic.base import ContextMixin 
# from django.views.generic import ListView, DetailView, UpdateView
# # from users.views import is_admin

# #variable for list of decorators
# decorators = [login_required, permission_required("tasks.change_task", login_url='no-permission')]

# #Class Based View Re-use example
# class Greetings(View):
#     greetings = 'Hello Everyone'
    
#     def get(self, request):
#         return HttpResponse(self.greetings)
    
# class HiGreetings(Greetings):
#     greetings = 'Hi Everyone'

# # Create your views here.

# def is_manager(user):
#     return user.groups.filter(name='Manager').exists()
# def is_employee(user):
#     return user.groups.filter(name='User').exists()
# def is_admin(user):
#     return user.groups.filter(name='Admin').exists()

# @user_passes_test(is_manager, login_url='no-permission')
# def manager_dashboard(request):
    
#     type = request.GET.get('type', 'all')
    
#     counts = Task.objects.aggregate(
#         total = Count('id'),
#         completed = Count('id', filter=Q(status='COMPLETED')),
#         in_progress = Count('id', filter=Q(status='IN_PROGRESS')),
#         pending = Count('id', filter=Q(status='PENDING'))
#     )
    
#     #Retriving Task Data
    
#     base_query = Task.objects.select_related('details').prefetch_related('assigned_to')
    
#     if type == 'completed':
#         tasks = base_query.filter(status='COMPLETED')
#     elif type == 'in-progress':
#         tasks = base_query.filter(status='IN_PROGRESS')
#     elif type == 'pending':
#         tasks = base_query.filter(status='PENDING')
#     elif type == 'all':
#         tasks = base_query.all()
    
#     context = {
#         "tasks" : tasks,
#         "counts" : counts,
#     }
    
#     return render(request, "dashboard/manager_dashboard.html", context)

# @user_passes_test(is_employee, login_url='no-permission')
# def employee_dashboard(request):
#     return render(request, "dashboard/user_dashboard.html")

# @login_required
# @permission_required("tasks.add_task", login_url='no-permission')
# def create_task(request):
#     # employees = Employee.objects.all()
#     task_form = TaskModelForm() #For GET
#     task_detail_form = TaskDetailModelForm()
#     if request.method == "POST":
#         task_form = TaskModelForm(request.POST) #For GET
#         task_detail_form = TaskDetailModelForm(request.POST)
        
#         if task_form.is_valid() and task_detail_form.is_valid():
            
#             ''' For Model Form Data '''
#             task = task_form.save()
#             task_detail = task_detail_form.save(commit=False)
#             task_detail.task = task
#             task_detail.save()
            
#             messages.success(request,"Task Created Successfully")
#             return redirect('create-task')
            
                
            
#     context = {"task_form": task_form, "task_detail_form": task_detail_form}
#     return render(request, "task_form.html", context)


# # create_decorators = [login_required, permission_required("tasks.change_task", login_url='no-permission')]
# class CreateTask(ContextMixin, View):
#     """ for creating task"""
#     required_permission = 'can_add_task'
#     login_url = 'sign-in'
#     template_name = 'task_form.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['task_form'] = TaskModelForm
#         context['task_detail_form'] = TaskDetailModelForm
#         return context
    
#     def get(self, request, *args, **kwargs):
#         context = self.get_context_data()
#         return render(request, self.template_name, context)
    
#     def post(self, request, *args, **kwargs):
#         task_form = TaskModelForm(request.POST) #For GET
#         task_detail_form = TaskDetailModelForm(request.POST)
        
#         if task_form.is_valid() and task_detail_form.is_valid():
            
#             ''' For Model Form Data '''
#             task = task_form.save()
#             task_detail = task_detail_form.save(commit=False)
#             task_detail.task = task
#             task_detail.save()
            
#             messages.success(request,"Task Created Successfully")
#             return redirect('create-task')
            


# @login_required
# @permission_required("tasks.change_task", login_url='no-permission')
# def update_task(request, id):
#     task = Task.objects.get(id=id)
#     task_form = TaskModelForm(instance=task) #For GET
#     if task.details:
#         task_detail_form = TaskDetailModelForm(instance=task.details)
#     if request.method == "POST":
#         task_form = TaskModelForm(request.POST, instance=task) 
#         task_detail_form = TaskDetailModelForm(request.POST, instance=task.details)
        
#         if task_form.is_valid() and task_detail_form.is_valid():
            
#             ''' For Model Form Data '''
#             task = task_form.save()
#             task_detail = task_detail_form.save(commit=False)
#             task_detail.task = task
#             task_detail.save()
            
#             messages.success(request,"Task Updated Successfully")
#             return redirect('dashboard')
            
                
            
#     context = {"task_form": task_form, "task_detail_form": task_detail_form}
#     return render(request, "task_form.html", context)


# update_task_decorators = [login_required, permission_required("tasks.update_task", login_url='no-permission')]

# @method_decorator(update_task_decorators, name='dispatch')
# class UpdateTask(UpdateView):
#     model = Task
#     form_class = TaskModelForm
#     template_name = 'task_form.html'
#     context_object_name = 'task'
#     pk_url_kwarg = 'id'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['task_form'] = self.get_form()
#         # print(context)
#         if hasattr(self.object, 'details') and self.object.details:
#             context['task_detail_form'] = TaskDetailModelForm(
#                 instance=self.object.details)
#         else:
#             context['task_detail_form'] = TaskDetailModelForm()

#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         task_form = TaskModelForm(request.POST, instance=self.object)

#         task_detail_form = TaskDetailModelForm(
#             request.POST, instance=getattr(self.object, 'details', None))

#         if task_form.is_valid() and task_detail_form.is_valid():

#             """ For Model Form Data """
#             task = task_form.save()
#             task_detail = task_detail_form.save(commit=False)
#             task_detail.task = task
#             task_detail.save()

#             messages.success(request, "Task Updated Successfully")
#             return redirect('update-task', self.object.id)
#         return redirect('update-task', self.object.id)


# @login_required
# @permission_required("tasks.delete_task", login_url='no-permission')
# def delete_task(request, id):
#     #get method diyeo kora jay delete handle but post diye kora recommended
#     if request.method == 'POST':
#         task = Task.objects.get(id=id)
#         task.delete()
#         messages.success(request, 'Task Deleted Successfully')
#         return redirect('manager-dashboard')
#     else:
#         messages.error(request, 'Something Went Wrong')
#         return redirect('manager-dashboard')
    

# # @login_required
# # @permission_required("tasks.view_task", login_url='no-permission')
# def view_task(request):
#     #Retrieve all data from Task Model
#     print("Fdsfsd")
#     view_task.required_permission = 'can_view_task'
#     tasks = Task.objects.all()
#     return render(request, "show_task.html", {"tasks": tasks})

# # @login_required
# # @permission_required("projects.view_project", login_url='no-permission')
# # def view_project(request):
# #     #project name and how many tasks it has
# #     projects = Project.objects.annotate(
# #         num_task = Count('task')).order_by('num_task')
# #     return render(request, "show_project.html", {"projects": projects})


# view_project_decorators = [login_required, permission_required("projects.view_project", login_url='no-permission')]

# @method_decorator(view_project_decorators, name='dispatch')
# class ViewProject(ListView): 
#     model = Project
#     context_object_name = "projects"
#     template_name = 'show_project.html'
    
#     def get_queryset(self):
#         queryset = Project.objects.annotate(
#             num_task = Count('task')).order_by('num_task')
#         return queryset
    

# @login_required
# @permission_required("tasks.view_task", login_url='no-permission')
# def task_details(request, task_id):
#     task = Task.objects.get(id=task_id)
#     status_choices = Task.STATUS_CHOICES
    
#     if request.method == 'POST':
#         selected_status = request.POST.get('task_status')
#         task.status = selected_status
#         task.save()
#         return redirect('task-details', task.id)
    
#     return render(request, 'task_details.html', {"task":task, 'status_choices': status_choices})


# task_detailview_decorators = [login_required, permission_required("tasks.view_task", login_url='no-permission')]

# @method_decorator(task_detailview_decorators, name='dispatch')
# class TaskDetail(DetailView):
#     model = Task
#     template_name = 'task_details.html'
#     context_object_name = 'task'
#     pk_url_kwarg = 'task_id'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs) #{"task":task}
#         context['status_choices'] = Task.STATUS_CHOICES #{"task":task, 'status_choices': status_choices}
#         return context
    
#     def post(self, request, *args, **kwargs):
#         task = self.get_object()
#         selected_status = request.POST.get('task_status')
#         task.status = selected_status
#         task.save()
#         return redirect('task-details', task.id)
    
    

# @login_required
# def dashboard(request):
#     if is_manager(request.user):
#         return redirect('manager-dashboard')
#     elif is_admin(request.user):
#         return redirect('admin-dashboard')
#     elif is_employee(request.user):
#         # return redirect('user-dashboard')
#         user = request.user
#         # today = date.today()

#         tasks = Task.objects.prefetch_related('assigned_to', 'details').filter(assigned_to=user)

#         todays_tasks = tasks.filter(
#             status__in=['PENDING', 'IN_PROGRESS']
#         ).order_by('due_date')

#         return render(request, 'dashboard/user_dashboard.html', {
#             'todays_tasks': todays_tasks,
#             'tasks': tasks,
#         })
        
#     return redirect('no-permission')


# @login_required
# def dashboard_view(request):
#     user = request.user
#     today = date.today()

#     tasks = Task.objects.prefetch_related('assigned_to', 'details').filter(assigned_to=user)

#     all_tasks = user.tasks.select_related('project').prefetch_related('assigned_to', 'details')
#     todays_tasks = Task.objects.filter(
#         assigned_to=user,
#         status__in=['PENDING', 'IN_PROGRESS']
#     ).order_by('due_date')

#     return render(request, 'dashboard/user_dashboard.html', {
#         'todays_tasks': todays_tasks,
#         'all_tasks': all_tasks,
#     })
    

#----userrole bsed ------

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from tasks.models import Task, TaskDetail, Project
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin
from django.views.generic import ListView, DetailView, UpdateView
from core.models import UserRole

# --- Role checkers using Custom Model Manager ---
def get_user_role(user):
    return UserRole.objects.get_role_name(user)

def has_custom_permission(user, code):
    return UserRole.objects.has_permission(user, code)

def require_custom_permission(permission_code):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not has_custom_permission(request.user, permission_code):
                return redirect('permission-denied')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# --- Views ---
@user_passes_test(lambda u: get_user_role(u) == 'Manager', login_url='permission-denied')
def manager_dashboard(request):
    type = request.GET.get('type', 'all')

    counts = {
        'total': Task.objects.count(),
        'completed': Task.objects.completed().count(),
        'in_progress': Task.objects.in_progress().count(),
        'pending': Task.objects.pending().count(),
    }   


    base_query = Task.objects.select_related('details').prefetch_related('assigned_to')
    print(base_query.query)
    tasks = base_query.all()

    if type == 'completed':
        tasks = Task.objects.completed()
    elif type == 'in-progress':
        tasks = Task.objects.in_progress()
    elif type == 'pending':
        tasks = Task.objects.pending()

    return render(request, "dashboard/manager_dashboard.html", {
        "tasks": tasks,
        "counts": counts,
    })

@user_passes_test(lambda u: get_user_role(u) == 'User', login_url='permission-denied')
def employee_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")

@login_required
@require_custom_permission("can_add_task")
def create_task(request):
    task_form = TaskModelForm()
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            return redirect('can_add_task')

    return render(request, "task_form.html", {
        "task_form": task_form,
        "task_detail_form": task_detail_form
    })

class CreateTask(ContextMixin, View):
    required_permission = 'can_add_task'
    login_url = 'sign-in'
    template_name = 'task_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not has_custom_permission(request.user, self.required_permission):
            return redirect('permission-denied')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = TaskModelForm
        context['task_detail_form'] = TaskDetailModelForm
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "Task Created Successfully")
        return redirect('can_add_task')

@login_required
@require_custom_permission("can_change_task")
def update_task(request, id):
    task = get_object_or_404(Task, id=id)
    task_form = TaskModelForm(instance=task)
    task_detail_form = TaskDetailModelForm(instance=getattr(task, 'details', None))

    if request.method == "POST":
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(request.POST, instance=task.details)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "Task Updated Successfully")
            return redirect('dashboard')

    return render(request, "task_form.html", {
        "task_form": task_form,
        "task_detail_form": task_detail_form
    })

@method_decorator([login_required, require_custom_permission("can_change_task")], name='dispatch')
class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        context['task_detail_form'] = TaskDetailModelForm(
            instance=getattr(self.object, 'details', None))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)
        task_detail_form = TaskDetailModelForm(request.POST, instance=getattr(self.object, 'details', None))

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "Task Updated Successfully")
        return redirect('update-task', self.object.id)

@login_required
@require_custom_permission("can_delete_task")
def delete_task(request, id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=id)
        task.delete()
        messages.success(request, 'Task Deleted Successfully')
    else:
        messages.error(request, 'Something Went Wrong')
    return redirect('manager-dashboard')

@require_custom_permission("can_view_task")
def view_task(request):
    type = request.GET.get('type', 'all')

    counts = {
        'total': Task.objects.count(),
        'completed': Task.objects.completed().count(),
        'in_progress': Task.objects.in_progress().count(),
        'pending': Task.objects.pending().count(),
    }

    if type == 'completed':
        tasks = Task.objects.completed()
    elif type == 'in-progress':
        tasks = Task.objects.in_progress()
    elif type == 'pending':
        tasks = Task.objects.pending()
    else:
        tasks = Task.objects.all()

    return render(request, "show_task.html", {
        "tasks": tasks,
        "counts": counts,
    })

@method_decorator([login_required, require_custom_permission("can_view_project")], name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = "projects"
    template_name = 'show_project.html'

    def get_queryset(self):
        return Project.objects.annotate(num_task=Count('task')).order_by('num_task')

@login_required
@require_custom_permission("can_view_task")
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == 'POST':
        task.status = request.POST.get('task_status')
        task.save()
        return redirect('task-details', task.id)

    return render(request, 'task_details.html', {'task': task, 'status_choices': status_choices})

@method_decorator([login_required, require_custom_permission("can_view_task")], name='dispatch')
class TaskDetail(DetailView):
    model = Task
    template_name = 'task_details.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        task.status = request.POST.get('task_status')
        task.save()
        return redirect('task-details', task.id)

@login_required
def dashboard(request):
    role = get_user_role(request.user)

    if role == 'Manager':
        return redirect('manager-dashboard')
    elif role == 'Admin':
        return redirect('admin-dashboard')
    elif role == 'User':
        user = request.user
        tasks = Task.objects.assigned_to(user)
        todays_tasks = tasks.filter(status__in=['PENDING', 'IN_PROGRESS']).order_by('due_date')

        return render(request, 'dashboard/user_dashboard.html', {
            'todays_tasks': todays_tasks,
            'tasks': tasks,
        })

    return redirect('permission-denied')

@login_required
def dashboard_view(request):
    user = request.user
    tasks = Task.objects.assigned_to(user).select_related('project').prefetch_related('assigned_to', 'details')
    todays_tasks = Task.objects.assigned_to(user).filter(
        status__in=['PENDING', 'IN_PROGRESS']
    ).order_by('due_date')

    return render(request, 'dashboard/user_dashboard.html', {
        'todays_tasks': todays_tasks,
        'all_tasks': tasks,
    })
