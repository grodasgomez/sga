
from django.http import HttpResponse
from django.shortcuts import render

def profile(request):
    return render(request, 'sga/profile.html')


def index(request):
    return render(request, 'sga/index.html')