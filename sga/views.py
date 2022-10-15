from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from django.dispatch.dispatcher import receiver
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages

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
    return render(request, 'sga/index.html')

@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, 'account/login.html')

#TODO: realizar html 404, no hay que redireccionar
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
