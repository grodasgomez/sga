from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views import generic
from projects.forms import FormCreateProject, FormCreateProjectMember, FormCreateUserStoryType

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


#User Story
class UserStoryTypeCreateView(LoginRequiredMixin, generic.View):
    def get(self, request, id):
        form = FormCreateUserStoryType(id)
        return render(request, 'user_story_type/create.html', {'form': form})

    def post(self, request, id):
        form = FormCreateUserStoryType(id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_user_story_type(project_id=id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario creado correctamente")
            
            return HttpResponseRedirect(f"/projects/{id}")
        return render(request, 'user_story_type/create.html', {'form': form})
