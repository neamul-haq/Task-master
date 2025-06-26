
from django.urls import path
from tasks.views import manager_dashboard, employee_dashboard, create_task, view_task, update_task, delete_task, task_details, dashboard,CreateTask, ViewProject, DetailView, UpdateTask

urlpatterns = [
    path('manager-dashboard/', manager_dashboard, name = "manager-dashboard"),
    path('user-dashboard/', employee_dashboard, name='user-dashboard'),
    path('create-task/', CreateTask.as_view(), name='can_add_task'),
    path('view-task/', view_task, name='can_view_task'),
    path('view-project/', ViewProject.as_view(), name='view-project'),
    path('task/<int:task_id>/details/', task_details, name='task-details'),
    path('update-task/<int:id>/', UpdateTask.as_view(), name='update-task'),
    path('delete-task/<int:id>/', delete_task, name='delete-task'),
    path('dashboard/', dashboard, name='dashboard'),
]