from django.views.generic import ListView, DetailView, FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect, render



from projects.mixin import ProjectPermissionMixin
from sprints.forms import SprintMemberCreateForm
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
    namespace = 'projects:sprints:index'

    def post(self, request, project_id):
        if(SprintUseCase.exists_created_sprint(project_id)):
            messages.warning(request, 'Ya existe un sprint planeado')
            return redirect(reverse(self.namespace, kwargs={'project_id': project_id}))

        SprintUseCase.create_sprint(project_id)
        messages.success(request, 'Sprint creado correctamente')
        return redirect(reverse(self.namespace, kwargs={'project_id': project_id}))

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

class SprintMemberCreateView(ProjectPermissionMixin, FormView):
    permissions = ['ABM Miembro Sprint']
    roles = ['Scrum Master']
    template_name = 'sprint-members/create.html'
    form_class = SprintMemberCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_id'] = self.kwargs.get('project_id')
        kwargs['sprint_id'] = self.kwargs.get('sprint_id')
        return kwargs

    def get_success_url(self):
        return reverse('projects:sprints:member-list', kwargs={
            'project_id': self.kwargs.get('project_id'),
            'sprint_id': self.kwargs.get('sprint_id'),
        })

    def form_valid(self, form):
        """
        Metodo que se ejecuta si el formulario es valido
        """
        data = form.cleaned_data
        sprint_id = self.kwargs.get('sprint_id')
        SprintUseCase.add_sprint_member(
            sprint_id=sprint_id,
            **data
        )
        messages.success(self.request, 'Usuario agregado al sprint correctamente')
        return super().form_valid(form)

class SprintMemberListView(ProjectPermissionMixin, View):
    permissions = ['ABM Miembro Sprint']
    roles = ['Scrum Master']

    def get(self, request, project_id, sprint_id):
        objects = SprintUseCase.get_sprint_members(sprint_id)
        sprint = Sprint.objects.get(id=sprint_id)
        context = {
            'project_id': project_id,
            'sprint_id': sprint_id,
            'sprint': sprint,
            'objects': objects,
        }
        print(context)
        return render(request, 'sprint-members/index.html', context)

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