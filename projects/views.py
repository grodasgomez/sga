from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.db.models.query import QuerySet

from projects.forms import FormCreateProject, FormCreateProjectMember, FormCreateUserStoryType, FormEditUserStoryType
from projects.models import Project, UserStoryType, ProjectStatus
from projects.usecase import ProjectUseCase
from users.models import CustomUser

# Create your views here.
class ProjectListView(LoginRequiredMixin, View):
    """
    Clase para mostrar los proyectos de acuerdo al usuario logueado
    """
    def get(self, request):
        user: CustomUser = request.user
        if not user.is_user():
            return HttpResponseRedirect('/')
        if user.is_admin():
            data = Project.objects.all()
            context = {
                'admin': True,
                'projects': data
            }
        else:
            context = {
                "admin": False,
                "projects": []
            }
            data = Project.objects.all()
            for p in data:
                if p.project_members.all().filter(id=user.id):
                    context['projects'].append(p)
        return render(request, 'projects/index.html', context)

class ProjectView(LoginRequiredMixin, View):
    def get(self, request, id):
        user: CustomUser = request.user
        if not user.is_user():
            return HttpResponseRedirect('/')
        data: Project = Project.objects.get(id=id)
        members: QuerySet = data.project_members.all()
        if user not in members:
            messages.warning(request, "No eres miembro")
            return HttpResponseRedirect('/projects')
        context= {
            "object" : data,
            "members" : members
        }
        return render(request, 'projects/project_detail.html', context)

    def post(self, request, id):
        data: Project = Project.objects.get(id=id)
        data.status = ProjectStatus.IN_PROGRESS
        data.save()
        messages.success(request, 'Proyecto iniciado correctamente')
        return redirect(request.META['HTTP_REFERER'])


class ProjectCreateView(LoginRequiredMixin, View):
    """
    Clase encargada de manejar la creacion de un proyecto
    """
    form_class = FormCreateProject

    def get(self, request):
        user: CustomUser = request.user
        if not user.is_admin():
            return HttpResponseRedirect('/')
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
    """
    Clase encargada de manejar la asignacion de miembros a un proyecto
    """
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


#User Story
class UserStoryTypeCreateView(LoginRequiredMixin, View):
    """
    Vista para crear un tipo de historia de usuario en un proyecto
    """
    def get(self, request, project_id):
        form = FormCreateUserStoryType(project_id)
        return render(request, 'user_story_type/create.html', {'form': form})

    def post(self, request, project_id):
        form = FormCreateUserStoryType(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_user_story_type(project_id=project_id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario creado correctamente")
            
            return HttpResponseRedirect(f"/projects/{project_id}/user-story-type")
        return render(request, 'user_story_type/create.html', {'form': form})

class UserStoryTypeEditView(LoginRequiredMixin, View):
    """
    Vista para editar un tipo de historia de usuario de un proyecto
    """
    def get(self, request, project_id, id):
        data = ProjectUseCase.get_user_story_type(id).__dict__
        data['columns'] = ",".join(data.get('columns'))
        print(project_id, id)
        form = FormEditUserStoryType(id, project_id, initial=data)
        return render(request, 'user_story_type/edit.html', {'form': form})

    def post(self, request, project_id, id):
        form = FormEditUserStoryType(id, project_id,request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.edit_user_story_type(id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario editado correctamente")
            
            return HttpResponseRedirect(f"/projects/{project_id}/user-story-type")
        return render(request, 'user_story_type/edit.html', {'form': form})

class UserStoryTypeListView(LoginRequiredMixin, ListView):
    """
    Vista que lista tipos de historias de usuario de un projecto
    """
    model = UserStoryType
    template_name = 'user_story_type/index.html'

    def get_queryset(self):
        return self.model.objects.filter(project_id=self.kwargs.get('project_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')

        #Convertimos las columnas de lista de str a un str separado por comas
        for item in context['object_list']:
            item.columns = ",".join(item.columns)
        return context
