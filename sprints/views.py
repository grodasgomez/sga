from django.views.generic import ListView, DetailView, FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.db.models.query import QuerySet



from projects.mixin import ProjectPermissionMixin
from users.models import CustomUser
from sprints.forms import SprintMemberCreateForm, SprintMemberEditForm, SprintStartForm, AssignSprintMemberForm
from sprints.models import Sprint, SprintMember
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

class SprintMemberEditView(ProjectPermissionMixin, FormView):
    permissions = ['ABM Miembro Sprint']
    roles = ['Scrum Master']
    template_name = 'sprint-members/edit.html'
    form_class = SprintMemberEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sprint_member = SprintMember.objects.get(id=self.kwargs.get('sprint_member_id'))
        kwargs['initial'] = {
            'workload': sprint_member.workload,
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sprint_member = SprintMember.objects.get(id=self.kwargs.get('sprint_member_id'))
        context['sprint_member'] = sprint_member
        return context
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
        sprint_member_id = self.kwargs.get('sprint_member_id')
        SprintUseCase.edit_sprint_member(
            sprint_member_id=sprint_member_id,
            workload=data['workload']
        )
        messages.success(self.request, 'Miembro editado correctamente')
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

class SprintStartView(ProjectPermissionMixin, FormView):
    """
    Vista para iniciar un sprint
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master']
    template_name = 'sprints/start.html'
    form_class = SprintStartForm

    def post(self, request, project_id):
        # SprintUseCase.create_sprint(project_id)
        messages.success(request, 'Proyecto creado correctamente')
        return redirect(reverse('projects:sprints:index', kwargs={'project_id': project_id}))

class SprintBacklogView(ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar el product Backlog de un Sprint
    """
    permissions = ['ABM US']#todo
    roles = ['Scrum Master']#todo

    def get(self, request, project_id, sprint_id):
        user: CustomUser = request.user
        if not user.is_user():
            messages.warning(request, "No eres un usuario verificado")
            return HttpResponseRedirect('/')
        members = SprintUseCase.get_sprint_members(sprint_id)
        print("members", members)
        # if user not in members:
        #     messages.warning(request, "No eres miembro del Sprint")
        #     return HttpResponseRedirect('/')

        user_stories = SprintUseCase.user_stories_by_sprint(sprint_id)

        #creo un Sprintmember
        context= {
            "user_stories" : user_stories,
            "project_id" : project_id,
            "sprint_id" : sprint_id
        }

        return render(request, 'sprints/backlog.html', context)

class SprintBacklogAssignView(ProjectPermissionMixin, View):
    """
    Clase encargada de asignar US en el product Backlog de un Sprint
    """
    form_class = AssignSprintMemberForm

    permissions = ['ABM Miembros']#todo
    roles = ['Scrum Master']#todo

    def get(self, request, project_id, sprint_id, user_story_id):
        form = self.form_class(sprint_id=sprint_id)
        return render(request, 'sprints/backlog_assign.html', {'form': form})

    def post(self, request, project_id, sprint_id, user_story_id):
        form = self.form_class(sprint_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            SprintUseCase.assign_sprint_member(user_story_id, **cleaned_data)
            messages.success(request, f"Miembro asignado correctamente")
            return HttpResponseRedirect('/sprints/{sprint_id}/backlog')
        return render(request, 'sprints/backlog_assign.html', {'form': form})