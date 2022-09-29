from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from users.forms import ProfileForm
from users.usecase import UserUseCase
from users.models import CustomUser
from django.views.generic import FormView
from sga.mixin import CustomLoginMixin, AdminMixin

# Create your views here.
class UsersView(AdminMixin, View):
    """
    Clase encargada de mostrar los usuarios y cambiar el rol de sistema
    """
    def get(self, request):
        user: CustomUser = request.user
        users = CustomUser.objects.all().exclude(id=user.id)
        context = {
            "users" :  users,
            "backpage": reverse("index")
        }
        return render(request, 'index.html', context)

    def post(self, request):
        #trae el user_id del boton presionado
        user_id = request.POST.get('user_id')
        if "user" in request.POST:
            UserUseCase.update_system_role(user_id, "user")
        if "admin" in request.POST:
            UserUseCase.update_system_role(user_id, "admin")
        return redirect(request.META['HTTP_REFERER'])

class ProfileView(CustomLoginMixin, FormView):
    """
    Vista para mostrar el perfil del usuario, asi como tambien para editar el perfil
    """
    # Nombre del template a renderizar
    template_name = 'profile.html'
    #Clase del formulario a utilizar
    form_class = ProfileForm
    # Indicamos el path al cual se redirecciona si el formulario es valido
    success_url = reverse_lazy("index")

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["backpage"] = reverse("index")
        return context
