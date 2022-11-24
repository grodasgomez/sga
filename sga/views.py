from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from django.dispatch.dispatcher import receiver
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages

from projects.models import Project
from sprints.usecase import SprintUseCase

@receiver(user_logged_in)
def user_logged_in_(request, **kwargs):
    """
    Limpia los mensajes antes de que el usuario inicie sesión
    """
    list(messages.get_messages(request))
    print("user_logged_in")

@receiver(user_logged_out)
def user_logged_out(request, **kwargs):
    """
    Limpia los mensajes immediatamente después de que un usuario cierra sesion
    """
    list(messages.get_messages(request))
    print("user_logged_out")

@never_cache
@login_required()
def index(request):
    if request.user.is_authenticated:
        projects = Project.objects.all()
        project_html = []
        for project in projects:
            if project.project_members.filter(id=request.user.id).exists() and (project.status == "CREATED" or project.status == "IN_PROGRESS"):
                sprint = SprintUseCase.get_current_sprint(project.id)
                project.name = project.name[:19] + "..." if len(project.name) > 22 else project.name
                if sprint:
                    project.sprint_id = sprint.id
                else:
                    project.sprint_id = None
                project_html.append(project)
        context = {"projects": project_html}
    return render(request, 'sga/index.html', context)

@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, 'account/login.html')

def custom_404(request, exception):
    messages.warning(request, "Página no encontrada")
    return redirect("/")

### SOLO PARA LOGEAR CON USUARIOS DE PRUEBA ###
from django.shortcuts import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from users.models import CustomUser
import os

@never_cache
def login_email(request):
    if request.user.is_authenticated:
        return redirect("/")
    if os.environ.get("DEBUG") == "0":
        return redirect(reverse("login"))
    email=request.POST.get("fname")
    try:
        user = CustomUser.objects.get(email=email)
        if not user.password:
            user.set_password("")
            user.save()
        auth_user = authenticate(email=email, password="")
        if auth_user:
            django_login(request, auth_user)
            return redirect("/")
    except:
        user = None
    return render(request, 'account/login_email.html')
