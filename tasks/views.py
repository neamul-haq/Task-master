
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
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib import admin
# --- Role checkers using Custom Model Manager ---
def get_user_role(user):
    return UserRole.objects.get_role_name(user)

def has_custom_permission(user, code):

    if not user.is_authenticated:
        return False

    # Generate a unique cache key for the user's permission
    cache_key = f"user:{user.id}:permission:{code}"
    

    cached_permission = cache.get(cache_key)
    
    if cached_permission is not None:
        print("✅ Permission checked from cache")
        return cached_permission  # Return cached result (True/False)
    
    has_permission = UserRole.objects.has_permission(user, code)
    print("🚨 DB hit for checking permission")
    # Cache the result in Redis with a TTL (e.g., 3600 seconds = 1 hour)
    cache.set(cache_key, has_permission, timeout=3600)
    
    return has_permission

def require_custom_permission(permission_code):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not has_custom_permission(request.user, permission_code):
                messages.error(request, "⚠️You do not have permission to access this page.")
                return redirect(request.META.get('HTTP_REFERER', 'home'))  # or redirect to any safe default
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# --- Views ---

def get_task_context(task_type, page_number):
    tasks_cache_key = f"task_list_{task_type}"
    counts_cache_key = "task_counts"
    cache_timeout = 60 * 5  # 5 minutes

    # Get tasks from cache or DB
    tasks = cache.get(tasks_cache_key)
    if not tasks:
        print("🚨 DB hit for task list")

        base_query = Task.objects.select_related('details').prefetch_related('assigned_to')
        if task_type == 'completed':
            tasks = list(base_query.completed())
        elif task_type == 'in_progress':
            tasks = list(base_query.in_progress())
        elif task_type == 'pending':
            tasks = list(base_query.pending())
        else:
            tasks = list(base_query.all())

        cache.set(tasks_cache_key, tasks, timeout=cache_timeout)
    else:
        print("✅ Task list from cache")

    # Get counts from cache or DB
    counts = cache.get(counts_cache_key)
    if not counts:
        print("🚨 DB hit for counts")
        counts = {
            'total': Task.objects.count(),
            'completed': Task.objects.completed().count(),
            'in_progress': Task.objects.in_progress().count(),
            'pending': Task.objects.pending().count(),
        }
        cache.set(counts_cache_key, counts, timeout=cache_timeout)
    else:
        print("✅ Counts from cache")

    paginator = Paginator(tasks, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "counts": counts,
        "task_type": task_type,
        "tasks": tasks
    }
    return context


@user_passes_test(lambda u: get_user_role(u) == 'Manager', login_url='permission-denied')
def manager_dashboard(request):
    return redirect('can_view_task')

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


@method_decorator(require_custom_permission('can_add_task'), name='dispatch')
class CreateTask(ContextMixin, View):
    template_name = 'task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employees = User.objects.all()
        context['task_form'] = TaskForm(employees=employees)
        context['task_detail_form'] = TaskDetailModelForm()
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        employees = User.objects.all()
        task_form = TaskForm(request.POST, employees=employees)
        task_detail_form = TaskDetailModelForm(request.POST)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "✅ Task Created Successfully")
            return redirect('can_add_task')
        else:
            messages.error(request, "❌ There was an error creating the task.")
            return render(request, self.template_name, {
                'task_form': task_form,
                'task_detail_form': task_detail_form
            })

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
    return redirect('can_view_task')



@require_custom_permission("can_view_task")
def view_task(request):
    task_type = request.GET.get('type', 'all')
    page = int(request.GET.get('page', 1))
    context = get_task_context(task_type, page)

    # Add JSON for Vue
    context["tasks_json"] = json.dumps([
        {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.details.priority if task.details else '',
            "priority_display": task.details.get_priority_display() if task.details else '',
            "created_at": task.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "assigned_to": [
                {
                    "first_name": user.first_name,
                    "full_name": user.get_full_name()
                } for user in task.assigned_to.all()
            ]
        } for task in context["tasks"]
    ], cls=DjangoJSONEncoder)

    return render(request, "show_task.html", context)


@method_decorator([login_required, require_custom_permission("can_view_project")], name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = "projects"
    template_name = 'show_project.html'

    def get_queryset(self):
        return Project.objects.annotate(num_task=Count('task')).order_by('num_task')

@login_required
@require_custom_permission("can_view_taskdetail")
def task_details(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == 'POST':
        task.status = request.POST.get('task_status')
        task.save()
        return redirect('task-details', task.id)

    return render(request, 'task_details.html', {'task': task, 'status_choices': status_choices})

@method_decorator([login_required, require_custom_permission("can_view_taskdetail")], name='dispatch')
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
    else:
        user = request.user
        tasks = Task.objects.assigned_to(user)
        tasks = tasks.filter(status__in=['PENDING', 'IN_PROGRESS']).order_by('due_date')
        todays_tasks = tasks.filter(due_date=timezone.now().date())
        return render(request, 'dashboard/user_dashboard.html', {
            'todays_tasks': todays_tasks,
            'tasks': tasks,
        })

    return redirect('permission-denied')

@login_required
def dashboard_view(request):
    # this is for user
    user = request.user
    tasks = Task.objects.assigned_to(user).select_related('project').prefetch_related('assigned_to', 'details')
    todays_tasks = Task.objects.assigned_to(user).filter(
        status__in=['PENDING', 'IN_PROGRESS']
    ).order_by('due_date')

    return render(request, 'dashboard/user_dashboard.html', {
        'todays_tasks': todays_tasks,
        'all_tasks': tasks,
    })
