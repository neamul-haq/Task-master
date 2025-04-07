from django.shortcuts import render
from django.http import HttpResponse
from tasks.forms import TaskForm, TaskModelForm
from tasks.models import Employee, Task
# Create your views here.

def manager_dashboard(request):
    tasks = Task.objects.all()
    
    #Getting task count
    total_task = tasks.count()
    pending_task = Task.objects.filter(status="PENDING").count()
    in_progress_task = Task.objects.filter(status="IN_PROGRESS").count()
    completed_task = Task.objects.filter(status="COMPLETED").count()
    
    context = {
        tasks : tasks,
        "total_task" : total_task,
        "pending_task" : pending_task,
        "completed_task" : completed_task,
        "in_progress_task": in_progress_task
    }
    
    return render(request, "dashboard/manager_dashboard.html", context)

def user_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")

def create_task(request):
    # employees = Employee.objects.all()
    form = TaskModelForm() #For GET
    if request.method == "POST":
        form = TaskModelForm(request.POST)
        if form.is_valid():
            
            ''' For Model Form Data '''
            form.save()
            return render(request, 'task_form.html', {"form": form, "message": "Task Added Successfully"})
            
                
            
    context = {"form": form}
    return render(request, "task_form.html", context)


def view_task(request):
    #Retrieve all data from Task Model
    tasks = Task.objects.all()
    return render(request, "show_task.html", {"tasks": tasks})