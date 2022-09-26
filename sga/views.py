from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from django.dispatch.dispatcher import receiver
from django.contrib.auth.signals import user_logged_out
from allauth.socialaccount.signals import pre_social_login
from django.contrib import messages

@receiver(pre_social_login)
def user_logged_in_(request, **kwargs):
    """
    Limpia los mensajes antes de que el usuario inicie sesión
    """
    print("user_logged_in")

@receiver(user_logged_out)
def user_logged_out(request, **kwargs):
    """
    Limpia los mensajes immediatamente después de que un usuario cierra sesion
    """
    list(messages.get_messages(request))
    print("user_logged_out")

@login_required()
def index(request):
    context = {"homepage" : True}
    return render(request, 'sga/index.html', context)

@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, 'account/login.html')