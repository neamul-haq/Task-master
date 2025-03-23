from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def show_task(request):
    return HttpResponse("Hello, world! This is a basic HttpResponse.")
