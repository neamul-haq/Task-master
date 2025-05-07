# tasks/templatetags/task_tags.py

from django import template
from tasks.models import Task

register = template.Library()

@register.simple_tag
def task_count_by_status(user, status=None):
    queryset = Task.objects.filter(assigned_to=user)
    if status:
        queryset = queryset.filter(status=status)
    return queryset.count()
