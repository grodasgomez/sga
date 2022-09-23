from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect



from projects.mixin import ProjectPermissionMixin
from sprints.models import Sprint
from sprints.usecase import SprintUseCase

class SprintListView(ProjectPermissionMixin, ListView):
    """
    Vista que lista tipos de historias de usuario de un projecto
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master']

    model = Sprint
    template_name = 'sprints/index.html'

    def get_queryset(self):
        return self.model.objects.filter(project_id=self.kwargs.get('project_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')

        return context

class SprintCreateView(ProjectPermissionMixin, View):
    """
    Vista para crear un nuevo sprint
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master']
    def post(self, request, project_id):
        # SprintUseCase.create_sprint(project_id)
        messages.success(request, 'Proyecto creado correctamente')
        return redirect(reverse('projects:sprints:index', kwargs={'project_id': project_id}))

class SprintView(ProjectPermissionMixin, DetailView):
    """
    Vista que lista tipos de historias de usuario de un projecto
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master', 'Developer', 'Product Owner']
    model = Sprint
    template_name = 'sprints/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')
        return context
class SprintStartView(ProjectPermissionMixin, View):
    """
    Vista para crear un nuevo sprint
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master']
    def post(self, request, project_id):
        # SprintUseCase.create_sprint(project_id)
        messages.success(request, 'Proyecto creado correctamente')
        return redirect(reverse('projects:sprints:index', kwargs={'project_id': project_id}))