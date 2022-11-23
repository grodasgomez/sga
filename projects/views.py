import json
from django.views.generic import ListView, FormView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views import View
from django.db.models.query import QuerySet
from django.urls import reverse
from django.http import JsonResponse, FileResponse
from django.forms.models import model_to_dict

from projects.forms import (FormCreateProject, FormCreateProjectMember, FormEditProjectMember, FormCreateUserStoryType, FormEditUserStoryType,
    FormCreateRole, ImportUserStoryTypeForm1, ImportUserStoryTypeForm2, FormCreateUserStory,FormEditUserStoryType, FormCreateRole,
    ImportUserStoryTypeForm1, ImportUserStoryTypeForm2,ImportRoleForm1, FormCreateUserStoryPO, FormEditUserStory, FormDeleteProject, FormCreateComment, FormCreateTask, FormCreateAttachment, FormCreateHoliday)
from projects.models import Project, UserStoryType, ProjectMember, ProjectStatus
from projects.usecase import ProjectUseCase, RoleUseCase
from sprints.mixin import SprintAccessMixin
from user_stories.models import UserStoryAttachment, UserStoryTask
from user_stories.usecase import UserStoriesUseCase
from projects.mixin import *
from sga.mixin import *
from users.models import CustomUser
from user_stories.models import UserStory, UserStoryStatus
from user_stories.mixin import UserStoryStatusMixin
from sprints.usecase import SprintUseCase
from sprints.models import Sprint, SprintStatus
from notifications.usecase import NotificationUseCase

# Create your views here.
class ProjectListView(VerifiedMixin, View):
    """
    Clase para mostrar los proyectos de acuerdo al usuario logueado,
    es una vista que todos los usuarios verificados pueden ver,
    pero solo los administradores pueden ver proyectos al cual no pertenecen
    """
    def get(self, request):
        user: CustomUser = request.user
        projects: Project = Project.objects.all().order_by('-end_date','-start_date')
        if user.is_admin():
            context = {
                'admin': True,
                'projects': projects
            }
        else:
            context = {
                "admin": False,
                "projects": []
            }
            for project in projects:
                if project.project_members.all().filter(id=user.id):
                    context['projects'].append(project)
        context["backpage"] = reverse("index")
        return render(request, 'projects/index.html', context)

class ProjectView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar los detalles de una view,
    es una vista que todos los miembros del proyecto pueden ver
    """
    def get(self, request, project_id):
        user = request.user
        project: Project = Project.objects.get(id=project_id)
        members: QuerySet = project.project_members.all()
        #TODO: modify_sprint_method
        can_start_project = ProjectUseCase.can_start_project(user.id, project_id)
        context= {
            "object" : project,
            "members" : members, #TODO: NO SE USA QUE HACE ESTO
            "can_start_project" : can_start_project,
            "backpage": reverse("projects:index")
        }
        return render(request, 'projects/project_detail.html', context)

    def post(self, request, project_id):
        ProjectUseCase.start_project(project_id)
        messages.success(request, 'Proyecto iniciado correctamente')
        return redirect(request.META['HTTP_REFERER'])

class ProjectMembersView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar los miembros de un proyecto,
    es una vista que todos los miembros del proyecto pueden ver
    """
    def get(self, request, project_id):
        data: Project = Project.objects.get(id=project_id)
        members: QuerySet = data.project_members.all()
        context= {
            "members" : [],
            "project_id" : project_id,
            "backpage": reverse("projects:project-detail", kwargs={"project_id": project_id})
        }
        #TODO: realizar un usecase get_project_members_with_roles()
        for member in members:
            scrum_master = False
            roles = RoleUseCase.get_roles_from_member(member, data)
            for role in roles:
                if role.name == "Scrum Master":
                    scrum_master = True
            context["members"].append({
                "project_member": member,
                "roles": RoleUseCase.get_roles_from_member(member, data),
                "scrum_master": scrum_master
            })
        return render(request, 'projects/project_members.html', context)

class ProjectCreateView(AdminMixin, View):
    """
    Clase encargada de manejar la creacion de un proyecto,
    solamente el administrador de sistemas tiene acceso a esta vista
    """
    form_class = FormCreateProject

    def get(self, request):
        form = self.form_class()
        context={
            "form": form,
            "backpage": reverse("projects:index")
        }
        return render(request, 'projects/create.html', context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_project(**cleaned_data)
            messages.success(request, 'Proyecto creado correctamente')
            return HttpResponseRedirect('/projects')
        return render(request, 'projects/create.html', {'form': form})

class ProjectDeleteView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar la cancelación de un proyecto
    """
    form_class = FormDeleteProject

    permissions = ['ABM Proyecto']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        project = Project.objects.get(id=project_id)
        data = vars(project)
        scrum_master = ProjectMember.objects.get(project=project, roles__name="Scrum Master")
        data['scrum_master']=scrum_master.user.email
        form = self.form_class(initial=data)
        context={
            "form": form,
            "backpage": reverse("projects:index")
        }
        return render(request, 'projects/delete.html', context)

    def post(self, request, project_id):
        project = ProjectUseCase.cancel_project(project_id)
        messages.success(request, f"Proyecto <strong>{project.name}</strong> cancelado correctamente")
        return redirect(reverse("projects:index"))

class ProjectMemberCreateView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar la asignacion de miembros a un proyecto
    """
    form_class = FormCreateProjectMember

    permissions = ['ABM Miembros']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = self.form_class(project_id=project_id)
        context={
            "form": form,
            "backpage": reverse("projects:project-members", kwargs={"project_id": project_id})
        }
        return render(request, 'project_member/create.html', context)

    def post(self, request, project_id):
        form = self.form_class(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            member = ProjectUseCase.add_member(project_id=project_id, **cleaned_data)
            NotificationUseCase.notify_add_member_to_project(member.user, member.project)
            messages.success(request, f"Miembro <strong>{cleaned_data['user'].email}</strong> agregado correctamente")
            return redirect(reverse("projects:project-members", kwargs={"project_id": project_id}))
        return render(request, 'project_member/create.html', {'form': form})

class ProjectRoleCreateView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar la creacion de roles
    """
    form_class = FormCreateRole

    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = self.form_class(project_id)
        context= {
            "form" : form,
            "project_id":project_id,
            "backpage": reverse("projects:index-roles", kwargs={"project_id": project_id})
        }
        return render(request, 'roles/create.html', context)

    def post(self, request, project_id):
        form=self.form_class(project_id,None,request.POST) #creamos un form con los datos cargados

        if form.is_valid(): #vemos si es valido
            cleaned_data=form.cleaned_data #tomamos los datos
            RoleUseCase.create_role(id=project_id, **cleaned_data)
            messages.success(request, f"Rol <strong>{cleaned_data['name']}</strong> creado correctamente")
            return HttpResponseRedirect('/projects/'+str(project_id)+'/roles')
        #si el form no es valido retorna a la misma pagina
        return render(request, 'roles/create.html', {'form': form, 'project_id':project_id})

class ProjectRoleView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar los roles de un proyecto
    """
    def get(self, request, project_id):
        #tomamos todos los roles del proyecto
        data = RoleUseCase.get_roles_by_project_no_default(project_id)
        context = {
            'roles': data,
            'project_id': project_id, #id del proyecto para usar en el template
            "backpage": reverse("projects:project-detail", kwargs={"project_id": project_id})
        }
        return render(request, 'roles/index.html', context) #le pasamos a la vista

class UserStoryTypeCreateView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Vista para crear un tipo de historia de usuario en un proyecto
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = FormCreateUserStoryType(project_id)
        context= {
            "form" : form,
            "backpage": reverse("projects:user-story-type-list", kwargs={"project_id": project_id})
        }
        return render(request, 'user_story_type/create.html', context)

    def post(self, request, project_id):
        form = FormCreateUserStoryType(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_user_story_type(project_id=project_id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario <strong>{cleaned_data['name']}</strong> creado correctamente")

            return HttpResponseRedirect(f"/projects/{project_id}/user-story-type")
        return render(request, 'user_story_type/create.html', {'form': form})

class UserStoryTypeEditView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Vista para editar un tipo de historia de usuario de un proyecto
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    def get(self, request, project_id, id):
        data = ProjectUseCase.get_user_story_type(id).__dict__
        columns_array=data.get('columns')
        columns_array=columns_array[1:-1]

        data['columns'] = ",".join(columns_array)

        form = FormEditUserStoryType(id, project_id, initial=data)
        context = {
            "form": form,
            "backpage": reverse("projects:user-story-type-list", kwargs={"project_id": project_id})
        }
        return render(request, 'user_story_type/edit.html', context)

    def post(self, request, project_id, id):
        form = FormEditUserStoryType(id, project_id,request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.edit_user_story_type(id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario <strong>{cleaned_data['name']}</strong> editado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/user-story-type")

        return render(request, 'user_story_type/edit.html', {'form': form})

class UserStoryTypeListView(CustomLoginMixin, ProjectAccessMixin, ListView):
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
        context['backpage'] = reverse('projects:project-detail', kwargs={'project_id': context['project_id']})
        return context

class ProjectRoleEditView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar la edicion de roles
    """
    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id, role_id):
        role = RoleUseCase.get_role_by_id(role_id)
        data = role.__dict__ #convertimos los datos del rol a un diccionario
        permissions= role.permissions.all()
        data['permissions']=permissions
        form = FormCreateRole(project_id,role_id,initial=data)
        context= {
            "form" : form,
            'role_id':role_id,
            'project_id':project_id,
            "backpage": reverse("projects:index-roles", kwargs={"project_id": project_id})
        }
        return render(request, 'roles/edit.html', context)

    def post(self, request, project_id, role_id):
        form = FormCreateRole(project_id,role_id,request.POST)
        if form.is_valid() and not RoleUseCase.role_is_in_use(role_id):
            cleaned_data = form.cleaned_data
            RoleUseCase.edit_role(role_id, **cleaned_data)
            messages.success(request, f"Rol <strong>{cleaned_data['name']}</strong> editado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/roles")

        role = RoleUseCase.get_role_by_id(role_id)
        data = role.__dict__ #convertimos los datos del rol a un diccionario
        permissions= role.permissions.all()
        data['permissions']=permissions
        form = FormCreateRole(project_id,role_id,initial=data)
        context= {
            "form" : form,
            'role_id':role_id,
            'project_id':project_id,
            "backpage": reverse("projects:index-roles", kwargs={"project_id": project_id})
        }
        messages.warning(request, f"El rol no se puede editar porque esta en uso")
        return render(request, 'roles/edit.html', context)

class ProjectRoleDeleteView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar el borrado de roles
    """
    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id, role_id):
        role = RoleUseCase.get_role_by_id(role_id)
        data = role.__dict__ #convertimos los datos del rol a un diccionario
        permissions= role.permissions.all()
        data['permissions']=permissions
        form = FormCreateRole(project_id,role_id,initial=data)
        context= {
            "form" : form,
            "role_id":role_id,
            "project_id":project_id,
            "backpage": reverse("projects:index-roles", kwargs={"project_id": project_id})
        }
        return render(request, 'roles/delete.html', context)

    def post(self, request, project_id, role_id):
        role = RoleUseCase.get_role_by_id(role_id)
        data = role.__dict__ #convertimos los datos del rol a un diccionario
        permissions= role.permissions.all()
        data['permissions']=permissions
        form = FormCreateRole(project_id,role_id,initial=data)
        context= {
            "form" : form,
            "role_id":role_id,
            "project_id":project_id,
            "backpage": reverse("projects:index-roles", kwargs={"project_id": project_id})
        }
        if not RoleUseCase.role_is_in_use(role_id):
            delete_role=RoleUseCase.delete_role(role_id)
            messages.success(request, f"Rol <strong>{delete_role.name}</strong> borrado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/roles")

        messages.warning(request, f"El rol no se puede borrar porque esta en uso")
        return render(request, 'roles/delete.html', context)

class ProjectMemberEditView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar la edicion de Miembro de proyecto
    """
    permissions = ['ABM Miembros']
    roles = ['Scrum Master']

    def get(self, request, project_id, member_id):
        member = RoleUseCase.get_project_member_by_id(member_id,project_id)
        data = member.__dict__
        roles= RoleUseCase.get_roles_from_member_id(member_id,project_id)
        for role in roles:
            if role.name == "Scrum Master":
                messages.warning(request, "El Scrum Master no puede ser editado")
                return HttpResponseRedirect(f"/projects/{project_id}/members")
        data['roles']=roles
        form = FormEditProjectMember(project_id,initial=data)
        context= {
            "form" : form,
            'member_id':member_id,
            'project_id':project_id,
            "backpage": reverse("projects:project-members", kwargs={"project_id": project_id})
        }
        return render(request, 'projects/project_member_edit.html', context)

    def post(self, request, project_id, member_id):
        form = FormEditProjectMember(project_id,request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            RoleUseCase.edit_project_member(member_id,project_id, **cleaned_data)
            messages.success(request, f"Miembro <strong>{cleaned_data['email']}</strong> editado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/members")

        return render(request, 'projects/project_member_edit.html', {'form': form, 'project_id':project_id, 'member_id':member_id})

class ProductBacklogView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar el product Backlog de un proyecto
    """
    def get(self, request, project_id):
        user: CustomUser = request.user
        user_stories = []
        us_type_filter_id = request.GET.get("type_us","")
        search = request.GET.get("search","")
        if us_type_filter_id != "" or search != "":
            us_type_filter_id = int(us_type_filter_id) if us_type_filter_id != "" else None
            user_stories = ProjectUseCase.user_stories_by_project_filter(project_id,us_type_filter_id,search)
        else:
            user_stories = ProjectUseCase.user_stories_by_project(project_id)

        user_story_types = ProjectUseCase.filter_user_story_type_by_project(project_id)
        context= {
            "search" : search,
            "us_type_filter_id" : us_type_filter_id,
            "user_story_types" : user_story_types,

            "user_stories" : user_stories,
            "project_id" : project_id,
            "backpage": reverse("projects:project-detail", kwargs={"project_id": project_id})
        }
        return render(request, 'backlog/index.html', context)

    def post(self, request, project_id):
        user_story_type_id = request.POST.get("filter","")
        search = request.POST.get("search","")

        search_exists = search != ""
        filter_exists = user_story_type_id != "empty"

        if search_exists and filter_exists:
            return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id})+'?type_us='+user_story_type_id+'&search='+search)
        elif search_exists:
            return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id})+'?search='+search)
        elif filter_exists:
            return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id})+'?type_us='+user_story_type_id)

        return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id}))

class ProductBacklogCreateView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de cargar el product Backlog de un proyecto
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master', 'Product Owner']

    def get(self, request, project_id):
        user = self.request.user
        has_perm = ProjectUseCase.member_has_permissions(user.id, project_id, self.permissions)
        has_role_SM = ProjectUseCase.member_has_roles(user.id, project_id, ['Scrum Master'])
        has_role_PO = ProjectUseCase.member_has_roles(user.id, project_id, ['Product Owner'])
        #TODO: solo se necesita preguntar si es PO, cualquier otro rol tiene formulario completo
        form = FormCreateUserStory(project_id)
        if has_perm or has_role_SM:
            form = FormCreateUserStory(project_id)
        elif (has_role_PO):
            form = FormCreateUserStoryPO(project_id)
        context= {
            "form" : form,
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        return render(request, 'backlog/create.html', context)

    def post(self, request, project_id):
        user = self.request.user
        has_perm = ProjectUseCase.member_has_permissions(user.id, project_id, self.permissions)
        has_role_SM = ProjectUseCase.member_has_roles(user.id, project_id, ['Scrum Master'])
        has_role_PO = ProjectUseCase.member_has_roles(user.id, project_id, ['Product Owner'])
        attachments = request.FILES.getlist('attachments')
        form = FormCreateUserStory(project_id, request.POST, request.FILES)
        if has_perm or has_role_SM:
            form = FormCreateUserStory(project_id, request.POST, request.FILES)
        elif (has_role_PO):
            form = FormCreateUserStoryPO(project_id, request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            if not ('technical_priority' in cleaned_data):
                cleaned_data['technical_priority'] = 0
            if not ('estimation_time' in cleaned_data):
                cleaned_data['estimation_time'] = 0
            cleaned_data['attachments'] = attachments
            code = Project.objects.get(id=project_id).prefix + "-" + str(ProjectUseCase.count_user_stories_by_project(project_id) + 1)
            ProjectUseCase.create_user_story(code, project_id=project_id, **cleaned_data)
            messages.success(request, f"Historia de usuario <strong>{cleaned_data['title']}</strong> creado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/backlog")

        return render(request, 'backlog/create.html', {'form': form})

class ProductBacklogCancelView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de cancelar una user story
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master']

    def get(self, request, project_id, us_id):
        us = ProjectUseCase.get_user_story_by_id(us_id)
        if us.status == UserStoryStatus.FINISHED:
            messages.warning(request, f"La historia de usuario <strong>{us.title}</strong> ya se encuentra finalizada")
        elif us.sprint:
            messages.warning(request, f"La historia de usuario <strong>{us.title}</strong> no se puede cancelar porque pertenece a un sprint")
        elif us.status == UserStoryStatus.CANCELLED:
            messages.warning(request, f"La historia de usuario <strong>{us.title}</strong> ya se encuentra cancelada")
        else:
            messages.success(request, f"La historia de usuario <strong>{us.title}</strong> se ha cancelado")
            us.status = UserStoryStatus.CANCELLED
            us.save()
        return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id}))

class UserStoryTypeImportView1(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, FormView):
    """
    Clase encargada de manejar la primera parte de la importacion de tipos de historias de usuario,
    seleccionando el proyecto de donde se importaran los tipos de historias de usuario
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    template_name = 'user_story_type/import1.html'
    form_class = ImportUserStoryTypeForm1

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project_id'] = self.kwargs.get('project_id')
        return kwargs

    def form_valid(self, form):
        from_project = form.cleaned_data['project']
        self.from_project_id = from_project.id
        self.project_id = self.kwargs.get('project_id')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['backpage'] = reverse("projects:user-story-type-list", kwargs={"project_id": self.kwargs["project_id"]})
        return context

    def get_success_url(self):
        return reverse('projects:user-story-type-import2', kwargs={'project_id': self.project_id, 'from_project_id': self.from_project_id})

class UserStoryTypeImportView2(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar la segunda parte de la importacion de tipos de historias de usuario,
    seleccionando los tipos de historias de usuario a importar
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    template_name = 'user_story_type/import2.html'

    def get(self, request, project_id, from_project_id):
        user_story_types = UserStoryType.objects.filter(project_id=from_project_id).exclude(name='Historia de Usuario')
        context = {
            'user_story_types': user_story_types,
            'project_id': project_id,
            'from_project_id': from_project_id,
            'form':{},
            "backpage": reverse("projects:user-story-type-import1", kwargs={"project_id": project_id})
        }
        return render(request, self.template_name, context)

    def post(self, request, project_id, from_project_id):
        form = ImportUserStoryTypeForm2(from_project_id, project_id,request.POST)
        if form.is_valid():
            user_story_types = form.cleaned_data['user_story_types']
            not_imported = form.cleaned_data['no_import_user_story_types']
            ProjectUseCase.import_user_story_types(project_id, from_project_id, user_story_types)

            get_name = lambda list: [x.name for x in list]
            imported_name = ", ".join(get_name(user_story_types))
            not_imported_name = ", ".join(get_name(not_imported))

            if imported_name:
                messages.success(request, f"Tipo/s de Historias de Usuario importado/s correctamente: {imported_name}")
            if not_imported_name:
                messages.warning(request, f"Tipo/s de Historia de Usuario no importado/s porque ya existe/n: {not_imported_name}")
            return redirect(reverse('projects:user-story-type-list', kwargs={'project_id': project_id}))

        # Obtengo el id con el tipo int de los tipos de historias de usuario que fueron seleccionados
        checked = list(map(int, request.POST.getlist('user_story_types')))
        context = {
            'user_story_types': UserStoryType.objects.filter(project_id=from_project_id).exclude(name='Historia de Usuario'),
            'project_id': project_id,
            'from_project_id': from_project_id,
            'checked':checked,
            'form':form
        }
        return render(request, self.template_name, context)

class RoleImportView1(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, FormView):
    """
    Clase encargada de manejar la primera parte de la importacion de roles,
    seleccionando el proyecto de donde se importaran los roles
    """
    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = ImportRoleForm1(project_id)
        context={
            "form":form,
            "backpage":reverse("projects:index-roles", kwargs={"project_id":project_id})
        }
        return render(request, 'roles/import1.html', context)

    def post(self, request, project_id):
        form = ImportRoleForm1(project_id, request.POST)
        context={
            "form":form,
            "backpage":reverse("projects:index-roles", kwargs={"project_id":project_id})
        }
        if form.is_valid():
            cleaned_data = form.cleaned_data
            from_project_id=cleaned_data.get('project').id
            return HttpResponseRedirect(f"/projects/{project_id}/roles/import/{from_project_id}")
        return render(request, 'roles/import1.html', context)

class RoleImportView2(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, FormView):
    """
    Clase encargada de manejar la segunda parte de la importacion de roles,
    seleccionando los roles a importar
    """
    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id, from_project_id):
        context={"roles":[]}

        roles_import=RoleUseCase.get_roles_by_project_no_default(from_project_id)

        for role in roles_import:
            context["roles"].append({"role":role, "permissions":role.permissions.all()})
        context["backpage"]=reverse("projects:import-role1", kwargs={"project_id":project_id})

        return render(request, 'roles/import2.html', context)

    def post(self, request, project_id, from_project_id):
        roles_import = request.POST.getlist("roles")
        if len(roles_import) == 0:
            messages.warning(request, "Debe seleccionar al menos un rol")
            return redirect(reverse('projects:import-role2', kwargs={'project_id': project_id, 'from_project_id': from_project_id}))

        roles_actual=RoleUseCase.get_roles_by_project_no_default(project_id)

        no_import=""
        yes_import=""
        project=Project.objects.get(id=from_project_id)

        for role_id in roles_import:
            role=RoleUseCase.get_role_by_id(role_id)
            skip_flag=False
            name_final=role.name+" (importado "+project.name+")"

            for role_actual in roles_actual:
                if role_actual.name==name_final:
                    no_import=no_import+role.name+","
                    skip_flag=True
                    break

            if not skip_flag:
                RoleUseCase.create_role(project_id, name_final, role.description, role.permissions.all())
                yes_import=yes_import+role.name+","

        if no_import!="":
            no_import = no_import[:-1]
            messages.warning(request, f"Rol/es no importado/s porque ya existe/n: {no_import}")
        if yes_import!="":
            yes_import = yes_import[:-1]
            messages.success(request, f"Rol/es importado/s correctamente: {yes_import}")

        return redirect(reverse('projects:index-roles', kwargs={'project_id': project_id}))

class ProductBacklogEditView(CustomLoginMixin, ProjectPermissionMixin, UserStoryStatusMixin, View):
    """
    Clase encargada de editar us en el product Backlog de un proyecto
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master']

    def get(self, request, project_id, us_id):
        user_story = ProjectUseCase.get_user_story_by_id(id=us_id)
        data=user_story.__dict__
        data['us_type']=user_story.us_type
        form = FormEditUserStory(project_id,initial=data)
        context= {
            "form" : form,
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        return render(request, 'backlog/edit.html', context)

    def post(self, request, project_id, us_id):

        form = FormEditUserStory(project_id,request.POST, request.FILES)
        context= {
            "form" : form,
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        if form.is_valid():
            cleaned_data = form.cleaned_data
            old_user_story = ProjectUseCase.get_user_story_by_id(id=us_id)
            #TODO: este retorna la us cambiada
            ProjectUseCase.edit_user_story(us_id, **cleaned_data)

            new_user_story = ProjectUseCase.get_user_story_by_id(id=us_id)
            UserStoriesUseCase.create_user_story_history(old_user_story, new_user_story, request.user, project_id)

            messages.success(request, f"Historia de usuario <strong>{cleaned_data['title']}</strong> editada correctamente")
            return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id}))

        return render(request, 'backlog/edit.html', context)

class UserStoryEditApiView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de editar la us
    """
    def put(self, request, project_id, us_id):
        data = json.loads(request.body)
        old_us = ProjectUseCase.get_user_story_by_id(id=us_id)
        new_us =ProjectUseCase.edit_user_story(us_id, **data)
        UserStoriesUseCase.create_user_story_history(old_us, new_us, request.user, project_id)

        # Notificamos al usuario asignado a la us si es que hay uno y no fue el que cambió la columna
        assigned_user = new_us.sprint_member.user
        logged_user = request.user
        if (assigned_user and logged_user.id != assigned_user.id):
            NotificationUseCase.notify_change_us_column(new_us, logged_user.email)

        # Notificamos a los scrum master del proyecto si la us se movió a la columna DONE
        if new_us.is_done:
            NotificationUseCase.notify_done_us(new_us)

        user_story = model_to_dict(new_us)
        tasks = UserStoryTask.objects.filter(user_story_id=us_id)
        for task in tasks :
            task.disabled = True
            print(f"Disabling tasks {task.user_story.code}-{task.description}")
            task.save()
        return JsonResponse({"data": user_story}, status=200)

class ProductBacklogDetailView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar el detalle de una us
    """
    def get(self, request, project_id, us_id):
        user_story = ProjectUseCase.get_user_story_by_id(id=us_id)
        attachments = ProjectUseCase.get_attachments_by_user_story(us_id)
        comments = UserStoriesUseCase.user_story_comments_by_us_id(us_id)
        tasks = UserStoriesUseCase.user_story_tasks_by_us_id(us_id)
        context = {
            "project_id": project_id,
            "user_story": user_story,
            "attachments": attachments,
            "comments" : comments,
            "tasks" : tasks,
            "backpage": reverse('projects:project-backlog', kwargs={'project_id': project_id})
        }
        return render(request, 'backlog/detail.html', context)

class UserStoryAttachmentDownloadView(CustomLoginMixin, ProjectAccessMixin, View):
    def get(self, request, project_id, us_id, attachment_id):
        attachment = UserStoryAttachment.objects.get(id=attachment_id)
        return FileResponse(open(attachment.file.path, 'rb'), content_type='application/force-download')

class ProductBacklogCreateCommentView(CustomLoginMixin, ProjectAccessMixin, UserStoryStatusMixin, View):
    """
    Clase encargada de agregar un comentarios a una US
    """
    form_class = FormCreateComment

    def get(self, request, project_id, us_id):
        user_story = UserStory.objects.get(id=us_id)
        form = self.form_class(us_id)
        context= {
            'user_story': user_story,
            "form" : form,
            "project_id":project_id,
            "us_id":us_id,
            "backpage": reverse('projects:project-backlog-detail', kwargs={'project_id': project_id, 'us_id':us_id })
        }
        return render(request, 'backlog/comment_create.html', context)

    def post(self, request, project_id, us_id):
        user_story = UserStory.objects.get(id=us_id)
        form=self.form_class(us_id,request.POST) #creamos un form con los datos cargados

        if form.is_valid(): #vemos si es valido
            cleaned_data=form.cleaned_data #tomamos los datos
            comment = UserStoriesUseCase.create_user_story_comment(us_id=us_id, user=request.user, project_id=project_id, **cleaned_data)
            us = comment.user_story

            if(us.sprint_member and us.sprint_member.id != request.user.id):
                NotificationUseCase.notify_comment_us(us)

            messages.success(request, f"Comentario creado correctamente")
            return redirect(reverse("projects:project-backlog-detail", kwargs={'project_id': project_id, 'us_id':us_id}))
        #si el form no es valido retorna a la misma pagina
        context= {
            'user_story': user_story,
            "form" : form,
            "project_id":project_id,
            "user_story_id":us_id,
            "backpage": reverse('projects:project-backlog-detail', kwargs={'project_id': project_id, 'us_id':us_id })
        }
        return render(request, 'backlog/comment_create.html', context)

class ProjectHolidayView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar los feriados de un proyecto
    """
    permissions = ['ABM Holidays']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        #tomamos todos los feriados del proyecto
        data = ProjectUseCase.get_holidays_by_project(project_id)
        context = {
            'holidays': data,
            'project_id': project_id, #id del proyecto para usar en el template
            'backpage': reverse("projects:project-detail", kwargs={"project_id": project_id})
        }
        return render(request, 'holidays/index.html', context) #le pasamos a la vista

class ProjectCreateHolidayView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de crear los feriados de un proyecto
    """
    permissions = ['ABM Holidays']
    roles = ['Scrum Master']

    form_class = FormCreateHoliday

    def get(self, request, project_id):
        form = self.form_class(project_id)
        context= {
            "form" : form,
            "project_id":project_id,
            "backpage": reverse("projects:index-holidays", kwargs={"project_id": project_id})
        }
        return render(request, 'holidays/create.html', context)

    def post(self, request, project_id):
        form=self.form_class(project_id,request.POST) #creamos un form con los datos cargados

        if form.is_valid(): #vemos si es valido
            cleaned_data=form.cleaned_data #tomamos los datos
            ProjectUseCase.create_holiday(project_id=project_id, **cleaned_data)

            SprintUseCase.recalculate_sprint_end_date(SprintUseCase.get_current_sprint(project_id))

            messages.success(request, f"Feriado <strong>{cleaned_data['date']}</strong> creado correctamente")
            return redirect(reverse("projects:index-holidays", kwargs={'project_id': project_id}))
        #si el form no es valido retorna a la misma pagina
        context= {
            "form" : form,
            "project_id":project_id,
            "backpage": reverse("projects:index-holidays", kwargs={"project_id": project_id})
        }
        return render(request, 'holidays/create.html', context)

class ProjectDeleteHolidayView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de manejar el borrado de feriados
    """
    permissions = ['ABM Holidays']
    roles = ['Scrum Master']

    def get(self, request, project_id, project_holiday_id):
        holiday = ProjectUseCase.get_holiday_by_id(project_holiday_id)
        data = holiday.__dict__ #convertimos los datos del feriado a un diccionario
        form = FormCreateHoliday(project_id,initial=data)
        context= {
            "form" : form,
            "project_holiday_id":project_holiday_id,
            "project_id":project_id,
            "backpage": reverse("projects:index-holidays", kwargs={"project_id": project_id})
        }
        return render(request, 'holidays/delete.html', context)

    def post(self, request, project_id, project_holiday_id):
        holiday = ProjectUseCase.get_holiday_by_id(project_holiday_id)
        data = holiday.__dict__ #convertimos los datos del feriado a un diccionario
        form = FormCreateHoliday(project_id,initial=data)
        context= {
            "form" : form,
            "project_holiday_id":project_holiday_id,
            "project_id":project_id,
            "backpage": reverse("projects:index-holidays", kwargs={"project_id": project_id})
        }
        if holiday:
            holiday.delete()

            SprintUseCase.recalculate_sprint_end_date(SprintUseCase.get_current_sprint(project_id))

            messages.success(request, f"Feriado <strong>{holiday.date}</strong> eliminado correctamente")
            return redirect(reverse("projects:index-holidays", kwargs={'project_id': project_id}))

        return render(request, 'holidays/delete.html', context)

class ProductBacklogCreateTaskView(CustomLoginMixin, ProjectStatusMixin, View):
    """
    Clase encargada de agregar un comentarios a una US,
    solo requiere de ProjectStatusMixin para que no se pueda
    agregar una tarea a una US de un proyecto finalizado/cancelado
    """
    form_class = FormCreateTask

    def get(self, request, project_id, us_id):
        user_story = UserStory.objects.get(id=us_id)
        if not user_story.sprint_member or not user_story.sprint_member.user == request.user:
            messages.warning(request, "No tiene permisos para realizar esta acción")
            return redirect(reverse('projects:board:index', kwargs={'project_id': project_id}))
        user_story = UserStory.objects.get(id=us_id)
        form = self.form_class(us_id)
        tasks_from_us = UserStoryTask.objects.filter(user_story_id=us_id)
        hours_worked = 0
        for task in tasks_from_us:
            hours_worked = hours_worked + task.hours_worked
        context= {
            'user_story': user_story,
            "form" : form,
            "project_id":project_id,
            "us_id":us_id,
            "hours_worked": hours_worked,
            "backpage": reverse('projects:board:index', kwargs={'project_id': project_id})
        }
        return render(request, 'backlog/task_create.html', context)

    def post(self, request, project_id, us_id):
        user_story = UserStory.objects.get(id=us_id)
        form=self.form_class(us_id,request.POST) #creamos un form con los datos cargados

        if form.is_valid(): #vemos si es valido
            cleaned_data=form.cleaned_data #tomamos los datos
            UserStoriesUseCase.create_user_story_task(user_story=user_story, user=request.user, **cleaned_data)
            messages.success(request, f"Tarea agregada correctamente")
            return redirect(reverse("projects:board:index", kwargs={'project_id': project_id}))
        #si el form no es valido retorna a la misma pagina
        context= {
            'user_story': user_story,
            "form" : form,
            "project_id":project_id,
            "user_story_id":us_id,
            "backpage": reverse('projects:board:index', kwargs={'project_id': project_id})
        }
        return render(request, 'backlog/task_create.html', context)

class ProductBacklogCreateAttachmentView(CustomLoginMixin, ProjectAccessMixin, UserStoryStatusMixin, FormView):
    template_name = 'backlog/attachment_create.html'
    form_class = FormCreateAttachment

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_story_id'] = self.kwargs.get('us_id')
        return kwargs

    def form_valid(self, form):
        attachments = self.request.FILES.getlist('attachments')
        us_id = self.kwargs.get('us_id')
        files = []
        for attachment in attachments:
            file = ProjectUseCase.create_attachment(us_id, attachment)
            files.append(file.filename)
        messages.success(self.request, f"Archivos <strong>{', '.join(files)}</strong> subidos correctamente")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_story'] = ProjectUseCase.get_user_story_by_id(id=self.kwargs.get('us_id'))
        context['backpage'] = reverse("projects:user-story-type-list", kwargs={"project_id": self.kwargs["project_id"]})
        return context

    def get_success_url(self):
        project_id = self.kwargs.get('project_id')
        return reverse('projects:project-backlog-detail', kwargs={'project_id': project_id, 'us_id':self.kwargs.get('us_id')})

class ProductBacklogDeleteAttachmentView(CustomLoginMixin, ProjectAccessMixin, UserStoryStatusMixin, View):
    def get(self, request, project_id, us_id, attachment_id):
        filename = ProjectUseCase.delete_attachment(attachment_id)
        messages.success(request, f"Archivo <strong>{filename}</strong> eliminado correctamente")
        return redirect(reverse('projects:project-backlog-detail', kwargs={'project_id': project_id, 'us_id':us_id}))

class ProductBacklogDeleteCommentView(CustomLoginMixin, ProjectAccessMixin, UserStoryStatusMixin, View):
    def get(self, request, project_id, us_id, comment_id):
        comment = UserStoriesUseCase.delete_user_story_comment(comment_id)
        messages.success(request, f"Comentario <strong>{comment.comment}</strong> eliminado correctamente")
        return redirect(reverse('projects:project-backlog-detail', kwargs={'project_id': project_id, 'us_id':us_id}))

class VelocityChartView(CustomLoginMixin, ProjectAccessMixin, View):
    """
    Clase encargada de mostrar el Velocity Chart de un proyecto
    """
    def get(self, request, project_id):
        project_sprints = ProjectUseCase.get_project_sprints(project_id)

        if not project_sprints:#todo esta bien la verificacion?
            messages.warning(request, "El Proyecto no tiene Sprints")
            return redirect(reverse("projects:project-detail", kwargs={"project_id": project_id}))

        estimated_hours_sprint = []
        worked_hours_sprint = []
        for sprint in project_sprints:
            if sprint.status != SprintStatus.CREATED:
                user_stories = UserStory.objects.filter(sprint_id=sprint.id)
                tasks = UserStoryTask.objects.filter(sprint_id=sprint.id)
                estimated_hours_sprint.append(sum([us.estimation_time for us in user_stories]))
                worked_hours_sprint.append(sum([task.hours_worked for task in tasks]))

        if len(estimated_hours_sprint) == 0 or len(worked_hours_sprint) == 0:
            messages.warning(request, "Aun no hay informacion de los Sprints para mostrar en el grafico")
            return redirect(reverse("projects:project-detail", kwargs={"project_id": project_id}))

        sprint_labels = []
        for x in range(1, len(estimated_hours_sprint)+1): sprint_labels.append(f"Sprint {x}")
        context= {
            "sprint_labels" : sprint_labels,
            "estimated_hours_sprint" : estimated_hours_sprint,
            "worked_hours_sprint" : worked_hours_sprint,
            "project_id" : project_id,
            "backpage": reverse("projects:project-detail", kwargs={"project_id": project_id})
        }
        return render(request, 'projects/velocity.html', context)
