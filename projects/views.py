from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views import generic

from projects.forms import FormCreateProject, FormCreateProjectMember, FormCreateRole

from projects.models import Project
from projects.models import Role
from projects.usecase import ProjectUseCase
from projects.usecase import RoleUseCase
from django.db.models import Q

#todo
from projects.models import Permission


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
            isRoleSave = ProjectUseCase.create_project(**cleaned_data)
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


class ProjectRoleCreaterView(LoginRequiredMixin, View):
    form_class = FormCreateRole
    isRoleSave=0 #variable para saber si se guardo o no algo recientemente
    #si ocurrio un envio de informacion POST

    def get(self, request, id):
        form = self.form_class()
        return render(request, 'roles/create.html', {'form': form,'project_id':id})

    def post(self, request, id):
        form=self.form_class(request.POST) #creamos un form con los datos cargados

        if form.is_valid(): #vemos si es valido
            cleaned_data=form.cleaned_data #tomamos los datos
            if RoleUseCase.create_role(id=id, **cleaned_data):
                messages.success(request, 'Rol creado correctamente')
                return HttpResponseRedirect('/projects/'+str(id)+'/roles')
            else:
                messages.warning(request, 'El rol ya existe')
        #si el form no es valido retorna a la misma pagina
        return render(request, 'roles/create.html', {'form': form, 'project_id':id})

class ProjectRoleView (LoginRequiredMixin, View): #Para ver  los roles
    def get(self, request, id):
        data = RoleUseCase.get_roles_by_project(id) #tomamos todos los roles del proyecto con esa id
        #data =  Role.objects.all().filter(Q(project=id) | Q(project=None)) #esta linea hace lo mismo
        context = { #ponemos en contextx
            'roles': data,
            'project_id': id #id del proyecto para usar en el template
        }
        return render(request, 'roles/index.html', context) #le pasamos a la vista
