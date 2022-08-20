
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def profile(request):
    print(request.user)
    return render(request, 'sga/profile.html')

@login_required()
def index(request):
    return render(request, 'sga/index.html')