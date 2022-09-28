from django.views.generic import ListView, DetailView, FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect

from projects.mixin import ProjectPermissionMixin
from users.models import CustomUser
from sprints.forms import SprintCreateForm, SprintMemberCreateForm, SprintMemberEditForm, SprintStartForm, AssignSprintMemberForm
from sprints.models import Sprint, SprintMember
from sprints.usecase import SprintUseCase
from user_stories.models import UserStory
from sga.mixin import NeverCacheMixin

class SprintListView(NeverCacheMixin, ProjectPermissionMixin, ListView):
    """
    Vista que lista tipos de historias de usuario de un projecto
    """
    permissions = ['ABM Sprint']
    roles = ['Scrum Master', 'Developer']

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

class SprintCreateView(NeverCacheMixin, ProjectPermissionMixin, FormView):
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
    # def post(self, request, project_id):
    #     if(SprintUseCase.exists_created_sprint(project_id)):
    #         messages.warning(request, 'Ya existe un sprint planeado')
    #         return redirect(reverse(self.namespace, kwargs={'project_id': project_id}))

    #     SprintUseCase.create_sprint(project_id)
    #     messages.success(request, 'Sprint creado correctamente')
    #     return redirect(reverse(self.namespace, kwargs={'project_id': project_id}))

class SprintView(NeverCacheMixin, ProjectPermissionMixin, DetailView):
    """
    Vista que lista tipos de historias de usuario de un projecto
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

class SprintMemberCreateView(NeverCacheMixin, ProjectPermissionMixin, FormView):
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

class SprintMemberEditView(NeverCacheMixin, ProjectPermissionMixin, FormView):
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

class SprintMemberListView(NeverCacheMixin, ProjectPermissionMixin, View):
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

class SprintStartView(NeverCacheMixin, ProjectPermissionMixin, FormView):
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

class SprintBacklogView(NeverCacheMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar el sprint Backlog
    """
    permissions = ['ABM US']#todo
    roles = ['Scrum Master', 'Developer']

    def get(self, request, project_id, sprint_id):
        user: CustomUser = request.user
        if not user.is_user():
            messages.warning(request, "No eres un usuario verificado")
            return HttpResponseRedirect('/')
        members = SprintUseCase.get_sprint_members(sprint_id)
        # if user not in members:
        #     messages.warning(request, "No eres miembro del Sprint")
        #     return HttpResponseRedirect('/')

        user_stories = SprintUseCase.user_stories_by_sprint(sprint_id)

        #creo un Sprintmember
        context= {
            "user_stories" : user_stories,
            "project_id" : project_id,
            "sprint_id" : sprint_id,
            "backpage": reverse("projects:sprints:detail", kwargs={"project_id": project_id, "sprint_id": sprint_id})
        }

        return render(request, 'sprints/backlog.html', context)

class SprintBacklogAssignMemberView(NeverCacheMixin, ProjectPermissionMixin, View):
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

class SprintBacklogAssignView(NeverCacheMixin, ProjectPermissionMixin, View):
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
        for us in user_stories:
            SprintUseCase.assign_us_sprint(sprint_id, us)
        return redirect(reverse("projects:sprints:backlog", kwargs={'project_id': project_id, 'sprint_id': sprint_id}))
