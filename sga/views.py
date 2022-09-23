from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@login_required()
def index(request):
    context = {"homepage" : True}
    return render(request, 'sga/index.html', context)

@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, 'account/login.html')