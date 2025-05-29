from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def no_permission(request):
    return render(request, 'no_permission.html')


def permission_denied(request):
    return render(request, 'permission_denied.html', status=403)

