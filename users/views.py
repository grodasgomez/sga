from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views import View
from users.forms import ProfileForm
from users.usecase import UserUseCase
from users.models import CustomUser
from django.views.generic import FormView

# Create your views here.
class UsersView(LoginRequiredMixin, View):
    def get(self, request):
        user: CustomUser = request.user
        if not user.is_admin():
            messages.warning(request, "No eres admin")
            return HttpResponseRedirect('/')
        custom_users = CustomUser.objects.all().exclude(id=user.id)
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

class ProfileView(LoginRequiredMixin, FormView):
    """
    Vista para mostrar el perfil del usuario, asi como tambien para editar el perfil
    """
    # Nombre del template a renderizar
    template_name = 'profile.html'

    #Clase del formulario a utilizar
    form_class = ProfileForm

    # Indicamos el path al cual se redirecciona si el formulario es valido
    success_url = '/profile'

    def get_form_kwargs(self):
        """
        Metodo para pasar el usuario logueado al formulario para indicar
        que el formulario es para editar, no para crear
        """
        #Obtenemos los parametros nombrados por defecto
        kwargs = super().get_form_kwargs()

        #Indicamos al form que es una edición, pasandole la instancia del usuario que se desea editar
        kwargs.update({'instance': self.request.user})

        return kwargs

    def form_valid(self, form):
        """
        Metodo que se ejecuta si el formulario es valido
        """
        user: CustomUser = self.request.user
        data = form.cleaned_data
        CustomUser.objects.filter(id=user.id).update(**data)
        messages.success(self.request, "Perfil actualizado")
        return super().form_valid(form)