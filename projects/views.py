from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.db.models.query import QuerySet

from projects.forms import FormCreateProject, FormCreateProjectMember
from projects.models import Project, ProjectMember, ProjectStatus
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
