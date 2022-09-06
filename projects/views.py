from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views import generic
from projects.forms import FormCreateProject, FormCreateProjectMember

from projects.models import Project
from projects.usecase import ProjectUseCase


# Create your views here.
class ProjectListView(LoginRequiredMixin, View):
    def get(self, request):
        data = Project.objects.all()
        context = {
            'projects': data
        }
        return render(request, 'projects/index.html', context)

class ProjectView(LoginRequiredMixin, generic.DetailView):
    model = Project
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.project_members.all()
        return context


class ProjectCreateView(LoginRequiredMixin, View):
    form_class = FormCreateProject

    def get(self, request):
        form = self.form_class()
        return render(request, 'projects/create.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_project(**cleaned_data)
            messages.success(request, 'Proyecto creado correctamente')
            
            return HttpResponseRedirect('/projects')
        return render(request, 'projects/create.html', {'form': form})


class ProjectMemberCreateView(LoginRequiredMixin, View):
    form_class = FormCreateProjectMember

    def get(self, request, id):
        form = self.form_class(project_id=id)
        return render(request, 'project_member/create.html', {'form': form})

    def post(self, request, id):
        form = self.form_class(id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.add_member(project_id=id, **cleaned_data)
            messages.success(request, f"Miembro agregado correctamente")
            
            return HttpResponseRedirect('/projects')
        return render(request, 'project_member/create.html', {'form': form})

def agg_roles(request):
    isRoleSave=0 #variable para saber si se guardo o no algo recientemente
    #si ocurrio un envio de informacion POST

    if request.method=="POST":
        formRolPost=FormRoles(request.POST) #creamos un form con los datos cargados
        if formRolPost.is_valid(): #vemos si es valido
            formRolNew=formRolPost.cleaned_data #tomamos los datos
            oldRole=Role.objects.all().filter(name=formRolNew['name_role']) #vemos si hay un rol en la bd con ese nombre
            if (len(oldRole)==0):
                newRole= Role(name=formRolNew['name_role'],description=formRolNew['description_role']) #creamos un rol
                newRole.save() #guardamos el rol en bd

                for perm in formRolNew['permissions']: #veremos cada permiso
                    #tomamos de la bd cada permiso con el id correspondiente
                    # permission_to_role=Permission.objects.get(id=perm)
                    #agregamos el permiso al rol nuevo
                    newRole.permissions.add(perm)

                isRoleSave=1 #se guardo un rol
            else:
                isRoleSave=2 #el rol ya existe
    #form vacio para el template
    #tomamos todos los permisos de la base de datos
    formRol = FormRoles()
    # formRol.fields['permissions'].choices=CHOICES #agregamos los permisos al form
    #enviamos el form vacio y el numero que indica si se cargo un rol o no
    return render(request, 'agg_roles.html', {'formRol': formRol,'isRoleSave':isRoleSave}) 
