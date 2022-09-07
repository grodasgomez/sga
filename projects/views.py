import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views import generic
from projects.forms import FormCreateProject, FormCreateProjectMember, FormCreateUserStoryType, FormEditUserStoryType

from projects.models import Project, UserStoryType
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


#User Story
class UserStoryTypeCreateView(LoginRequiredMixin, generic.View):
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

class UserStoryTypeEditView(LoginRequiredMixin, generic.View):
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

class UserStoryTypeListView(LoginRequiredMixin, generic.ListView):
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
