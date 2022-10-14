from django.views.generic import ListView, DetailView, FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
import itertools
from projects.mixin import ProjectPermissionMixin, ProjectAccessMixin
from projects.models import UserStoryType
from users.models import CustomUser
from sprints.forms import SprintCreateForm, SprintMemberCreateForm, SprintMemberEditForm, SprintStartForm, AssignSprintMemberForm
from sprints.models import Sprint, SprintMember
from sprints.usecase import SprintUseCase
from user_stories.models import UserStory
from sga.mixin import CustomLoginMixin

class SprintListView(CustomLoginMixin, ProjectAccessMixin, ListView):
    """
    Vista que lista los sprints de un proyecto
    """
    model = Sprint
    template_name = 'sprints/index.html'

    def get_queryset(self):
        return self.model.objects.filter(project_id=self.kwargs.get('project_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')
        context['backpage'] = reverse('projects:project-detail', kwargs={'project_id': context['project_id']})

        return context

class SprintCreateView(CustomLoginMixin, ProjectPermissionMixin, FormView):
    """
    Vista para crear un nuevo sprint
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master']

    form_class = SprintCreateForm
    template_name = 'sprints/create.html'

    def get(self, request, project_id, **kwargs):
        if(SprintUseCase.exists_created_sprint(project_id)):
            messages.warning(request, 'Ya existe un sprint en planeación')
            return redirect(reverse('projects:sprints:index', kwargs={'project_id': project_id}))
        return super().get(request, project_id, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_id'] = self.kwargs.get('project_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')
        context['backpage'] = reverse('projects:sprints:index', kwargs={'project_id': context['project_id']})
        return context

    def form_valid(self, form):
        # Creamos el sprint
        data = form.cleaned_data
        project_id = self.kwargs.get('project_id')
        SprintUseCase.create_sprint(project_id, **data)
        messages.success(self.request, 'Sprint creado con éxito')
        return super().form_valid(form)

    def get_success_url(self):
        namespace = 'projects:sprints:index'
        return reverse(namespace, kwargs={'project_id': self.kwargs.get('project_id')})

class SprintView(CustomLoginMixin, ProjectPermissionMixin, DetailView):
    """
    Vista que lista los detalles de un sprint
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master', 'Developer', 'Product Owner']
    model = Sprint
    template_name = 'sprints/detail.html'
    # Indicamos el pk del objeto
    pk_url_kwarg = 'sprint_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')
        context['backpage'] = reverse('projects:sprints:index', kwargs={'project_id': context['project_id']})
        return context

class SprintMemberCreateView(CustomLoginMixin, ProjectPermissionMixin, FormView):
    """
    Vista para crear miembro de un sprint
    """
    permissions = ['ABM Miembro Sprint']
    roles = ['Scrum Master']

    template_name = 'sprint-members/create.html'
    form_class = SprintMemberCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_id'] = self.kwargs.get('project_id')
        kwargs['sprint_id'] = self.kwargs.get('sprint_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        context['project_id'] = self.kwargs.get('project_id')
        context['backpage'] = reverse('projects:sprints:index', kwargs={'project_id': context['project_id']})
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
        sprint_id = self.kwargs.get('sprint_id')
        SprintUseCase.add_sprint_member(
            sprint_id=sprint_id,
            **data
        )
        messages.success(self.request, f"Usuario <strong>{data['user']}</strong> agregado al sprint correctamente")
        return super().form_valid(form)

class SprintMemberEditView(CustomLoginMixin, ProjectPermissionMixin, FormView):
    """
    Vista para editar miembro de un sprint
    """
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
        context['backpage'] = reverse('projects:sprints:member-list', kwargs={'project_id': self.kwargs.get('project_id'), 'sprint_id': self.kwargs.get('sprint_id')})
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
        sprint_member_data=SprintUseCase.edit_sprint_member(
            sprint_member_id=sprint_member_id,
            workload=data['workload']
        )
        messages.success(self.request, f"Miembro <strong>{sprint_member_data.user.email}</strong> editado correctamente")
        return super().form_valid(form)

class SprintMemberListView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Vista para listar los miembros de un sprint
    """
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
            'backpage': reverse("projects:sprints:detail", kwargs={"project_id": project_id, "sprint_id": sprint_id}),
        }
        return render(request, 'sprint-members/index.html', context)

class SprintStartView(CustomLoginMixin, ProjectPermissionMixin, FormView):
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

class SprintBacklogView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar el sprint Backlog
    """
    permissions = ['ABM US']#todo
    roles = ['Scrum Master', 'Developer']

    def get(self, request, project_id, sprint_id):
        members = SprintUseCase.get_sprint_members(sprint_id)
        user_stories = SprintUseCase.user_stories_by_sprint(sprint_id)

        #creo un Sprintmember
        context= {
            "user_stories" : user_stories,
            "project_id" : project_id,
            "sprint_id" : sprint_id,
            "backpage": reverse("projects:sprints:detail", kwargs={"project_id": project_id, "sprint_id": sprint_id})
        }

        return render(request, 'sprints/backlog.html', context)

class SprintBacklogAssignMemberView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de asignar una US a un miembro del sprint
    """
    form_class = AssignSprintMemberForm

    permissions = ['ABM US Miembro Sprint']
    roles = ['Scrum Master']

    def get(self, request, project_id, sprint_id, user_story_id):
        try:
            sprint_member = SprintMember.objects.get(userstory=user_story_id)
        except SprintMember.DoesNotExist:
            sprint_member = None
        form = self.form_class(sprint_id=sprint_id,initial={'sprint_member': sprint_member})

        return render(request, 'sprints/backlog_assign_member.html', {'form': form})

    def post(self, request, project_id, sprint_id, user_story_id):
        form = self.form_class(sprint_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            SprintUseCase.assign_us_sprint_member(**cleaned_data, user_story_id=user_story_id)
            us_data=UserStory.objects.get(id=user_story_id)
            messages.success(request, f"Miembro <strong>{cleaned_data['sprint_member']}</strong> asignado correctamente al US <strong>{us_data.title}</strong>")
            return redirect(reverse('projects:sprints:backlog', kwargs={'project_id': project_id, 'sprint_id': sprint_id}))
        return render(request, 'sprints/backlog_assign_member.html', {'form': form})

class SprintBacklogAssignView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de asignar una US del product backlog al sprint
    """
    permissions = ['ABM US Sprint']
    roles = ['Scrum Master']

    def get(self, request, project_id, sprint_id):
        user_stories = SprintUseCase.assignable_us_to_sprint(project_id, sprint_id)
        if not user_stories:
            messages.warning(request, "No hay US disponibles para asignar")
            return redirect(reverse('projects:sprints:backlog', kwargs={'project_id': project_id, 'sprint_id': sprint_id}))
        context = {
            "user_stories": user_stories
        }
        return render(request, 'sprints/backlog_assign_us.html', context)

    def post(self, request, project_id, sprint_id):
        user_stories = request.POST.getlist("us")
        assigned_names = []
        for us in user_stories:
            us = SprintUseCase.assign_us_sprint(sprint_id, us)
            assigned_names.append(us.code)
        message = ', '.join(assigned_names)
        messages.success(request, f"Historia/s de Usuario asignada/s correctamente: {message}")
        return redirect(reverse("projects:sprints:backlog", kwargs={'project_id': project_id, 'sprint_id': sprint_id}))


class SprintBoardView(View):
    def get(self, request, project_id):
        sprint = Sprint.objects.filter(project_id=project_id).first()
        user_stories = UserStory.objects.filter(sprint_id=sprint.id).all()
        us_types = UserStoryType.objects.filter(project_id=project_id).all()

        context = {
            'project_id': project_id,
            'sprint': sprint,
            'user_stories': [us.to_kanban_item() for us in user_stories],
            'us_types': [model_to_dict(us_type) for us_type in us_types],
        }
        return render(request, 'sprints/board.html', context)
