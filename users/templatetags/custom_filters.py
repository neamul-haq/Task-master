from django import template
from datetime import datetime
from django.utils import timezone

register = template.Library()


@register.filter
def humanized_date(value):
    if value:
        today = datetime.now().date()
        value = timezone.localtime(value)
        if value.date() == today:
            return f"Today at {value.strftime('%I:%M %p')}"
        if value.date() == today.replace(day=today.day - 1):
            return f"Yesterday at {value.strftime('%I:%M %p')}"
        else:
            return f"{value.date().strftime('%B %d')}, {value.strftime('%I:%M %p')}"
    return "No login record available"


@register.filter
def round_val(value, digits=0):
    
    try:
        return round(float(value), int(digits))
    except (ValueError, TypeError):
        return value

@register.filter
def add(value, arg):

    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):

    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):

    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):

    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return "∞"