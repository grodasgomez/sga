from django.views.generic import ListView, DetailView, FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect, render
from django.forms.models import model_to_dict
from projects.mixin import *
from projects.models import UserStoryType, ProjectStatus
from projects.usecase import ProjectUseCase
from users.models import CustomUser
from sprints.forms import SprintCreateForm, SprintMemberCreateForm, SprintMemberEditForm, SprintStartForm, AssignSprintMemberForm
from sprints.models import Sprint, SprintMember
from sprints.usecase import *
from sprints.mixin import *
from user_stories.usecase import UserStoriesUseCase
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

class SprintCreateView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, FormView):
    """
    Vista para crear un nuevo sprint
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master']

    form_class = SprintCreateForm
    template_name = 'sprints/create.html'

    def get(self, request, project_id, **kwargs):
        # Si el proyecto no esta en planeacion, no se puede crear un sprint
        if not ProjectUseCase.get_project_status(project_id) == ProjectStatus.IN_PROGRESS:
            messages.warning(request, 'El proyecto aun no fue iniciado')
            return redirect(reverse('projects:sprints:index', kwargs={'project_id': project_id}))
        # Si ya existe un sprint en planeacion, no se puede crear otro
        if SprintUseCase.exists_created_sprint(project_id):
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

class SprintView(CustomLoginMixin, SprintAccessMixin, DetailView):
    """
    Vista que lista los detalles de un sprint
    """
    model = Sprint
    template_name = 'sprints/detail.html'
    # Indicamos el pk del objeto
    pk_url_kwarg = 'sprint_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos el id del proyecto en el contexto para ser usado en el template
        project_id = self.kwargs.get('project_id')
        context['project_id'] = project_id
        context['backpage'] = reverse('projects:sprints:index', kwargs={'project_id': context['project_id']})
        if self.is_scrum_master:
            context['modify_sprint_status'] = True
        else:
            context['modify_sprint_status'] = ProjectUseCase.member_has_permissions(self.request.user.id, project_id, ["ABM Sprint"])
        return context

    def post(self, request, project_id, sprint_id):
        sprint = super().get_object()
        try:
            if sprint.status == "PLANNED":
                SprintUseCase.start_sprint(sprint)
                messages.success(request, f"Sprint iniciado correctamente")
            elif sprint.status == "IN_PROGRESS":
                SprintUseCase.finish_sprint(sprint, request.user, self.kwargs.get('project_id'))
                messages.success(request, f"Sprint finalizado correctamente, prioridad de las historias de usuario actualizada")
        except CustomError as e:
            messages.warning(request, e)
        return redirect(reverse('projects:sprints:detail', kwargs={'project_id': project_id, 'sprint_id': sprint_id}))

class SprintMemberCreateView(CustomLoginMixin, ProjectPermissionMixin, SprintStatusMixin, FormView):
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

class SprintMemberEditView(CustomLoginMixin, ProjectPermissionMixin, SprintStatusMixin, FormView):
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

class SprintMemberListView(CustomLoginMixin, SprintAccessMixin, View):
    """
    Vista para listar los miembros de un sprint
    """
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

class SprintBacklogView(CustomLoginMixin, SprintAccessMixin, View):
    """
    Clase encargada de mostrar el sprint Backlog
    """
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

class SprintBacklogAssignMemberView(CustomLoginMixin, ProjectPermissionMixin, SprintStatusMixin, View):
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
        assignable_members = SprintUseCase.get_assignable_sprint_members(sprint_id)
        assignable_members = [ member.to_assignable_data() for member in assignable_members]
        us_estimation = UserStory.objects.get(id=user_story_id).estimation_time
        context = {
            'form': form,
            'us_estimation': us_estimation,
            'assignable_members': assignable_members,
            'backpage': reverse('projects:sprints:backlog', kwargs={'project_id': project_id, 'sprint_id': sprint_id}),
        }
        return render(request, 'sprints/backlog_assign_member.html', context)

    def post(self, request, project_id, sprint_id, user_story_id):
        form = self.form_class(sprint_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            old_us=ProjectUseCase.get_user_story_by_id(user_story_id)
            SprintUseCase.assign_us_sprint_member(**cleaned_data, user_story_id=user_story_id)
            us_data=UserStory.objects.get(id=user_story_id)
            UserStoriesUseCase.create_user_story_history(old_us, us_data, request.user, project_id)
            messages.success(request, f"Miembro <strong>{cleaned_data['sprint_member']}</strong> asignado correctamente al US <strong>{us_data.title}</strong>")
            return redirect(reverse('projects:sprints:backlog', kwargs={'project_id': project_id, 'sprint_id': sprint_id}))
        return render(request, 'sprints/backlog_assign_member.html', {'form': form})

class SprintBacklogAssignView(CustomLoginMixin, ProjectPermissionMixin, SprintStatusMixin, View):
    """
    Clase encargada de asignar una US del product backlog al sprint
    """
    permissions = ['ABM US Sprint']
    roles = ['Scrum Master']

    def get(self, request, project_id, sprint_id):
        user_stories = SprintUseCase.assignable_us_to_sprint(project_id, sprint_id).order_by('-sprint_priority')
        if not user_stories:
            messages.warning(request, "No hay US disponibles para asignar")
            return redirect(reverse('projects:sprints:backlog', kwargs={'project_id': project_id, 'sprint_id': sprint_id}))
        sprint = Sprint.objects.get(id=sprint_id)
        available_capacity = sprint.capacity - sprint.used_capacity
        context = {
            "sprint": sprint,
            "available_capacity": available_capacity,
            "user_stories": user_stories,
            "backpage": reverse("projects:sprints:backlog", kwargs={"project_id": project_id, "sprint_id": sprint_id})
        }
        return render(request, 'sprints/backlog_assign_us.html', context)

    def post(self, request, project_id, sprint_id):
        user_stories = request.POST.getlist("us")
        assigned_names = []
        for us in user_stories:
            old_us=ProjectUseCase.get_user_story_by_id(us)
            us = SprintUseCase.assign_us_sprint(sprint_id, us)
            UserStoriesUseCase.create_user_story_history(old_us, us, request.user, project_id)
            assigned_names.append(us.code)
        message = ', '.join(assigned_names)
        messages.success(request, f"Historia/s de Usuario asignada/s correctamente: {message}")
        return redirect(reverse("projects:sprints:backlog", kwargs={'project_id': project_id, 'sprint_id': sprint_id}))


class SprintBoardView(CustomLoginMixin, ProjectAccessMixin, View):
    def get(self, request, project_id):
        sprint = SprintUseCase.get_current_sprint(project_id)
        if not sprint:
            messages.warning(request, "No hay sprint en progreso para este proyecto")
            return redirect(reverse("projects:project-detail", kwargs={"project_id": project_id}))

        user_stories = UserStory.objects.filter(sprint_id=sprint.id).all()
        us_types = UserStoryType.objects.filter(project_id=project_id).all()

        context = {
            'project_id': project_id,
            'sprint': sprint,
            'user_stories': [us.to_kanban_item() for us in user_stories],
            'us_types': [model_to_dict(us_type) for us_type in us_types],
        }
        return render(request, 'sprints/board.html', context)

class SprintBacklogMoreInformationView(CustomLoginMixin, SprintAccessMixin, View):
    def get(self, request, project_id, sprint_id, user_story_id):
        user_story = UserStory.objects.get(id=user_story_id)
        context = {
            'user_story': user_story,
            'backpage': reverse('projects:sprints:backlog', kwargs={'project_id': project_id, 'sprint_id': sprint_id})
        }
        return render(request, 'sprints/backlog_more_information.html', context)
