from multiprocessing import context
from random import choices
from django.shortcuts import render, redirect
from django.http import HttpResponse
#importo project de projecto models
from projects.models import Project
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views import View
from users.usecase import UserUseCase
from users.models import CustomUser

# Create your views here.
class UsersView(LoginRequiredMixin, View):
    def get(self, request):
        user: CustomUser = request.user
        if not user.is_admin():
            messages.warning(request, "No eres admin")
            return HttpResponseRedirect('/')
        custom_users = CustomUser.objects.all()
        users = [user for user in custom_users]
        context = { "users" :  users }

        return render(request, 'index.html', context)


    def post(self, request):
        #trae el value del boton con name user
        user_id = request.POST.get('user_id')
        if (int(request.user.id) == int(user_id)):
            messages.warning(request, "No puedes cambiar tu rol")
        else:
            if "user" in request.POST:
                UserUseCase.update_system_role(user_id, "user")
            if "admin" in request.POST:
                UserUseCase.update_system_role(user_id, "admin")
        return redirect(request.META['HTTP_REFERER'])
