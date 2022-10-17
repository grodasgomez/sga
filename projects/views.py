import json
from django.views.generic import ListView, FormView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views import View
from django.db.models.query import QuerySet
from django.urls import reverse
from django.http import JsonResponse
from django.forms.models import model_to_dict


from projects.forms import (FormCreateProject, FormCreateProjectMember, FormEditProjectMember, FormCreateUserStoryType, FormEditUserStoryType,
    FormCreateRole, ImportUserStoryTypeForm1, ImportUserStoryTypeForm2, FormCreateUserStory,FormEditUserStoryType, FormCreateRole,
    ImportUserStoryTypeForm1, ImportUserStoryTypeForm2,ImportRoleForm1, FormCreateUserStoryPO, FormEditUserStory, FormDeleteProject)
from projects.models import Project, UserStoryType, ProjectMember, ProjectStatus
from projects.usecase import ProjectUseCase, RoleUseCase
from user_stories.usecase import UserStoriesUseCase
from projects.mixin import *
from sga.mixin import *
from users.models import CustomUser

# Create your views here.
class ProjectListView(VerifiedMixin, View):
    """
    Clase para mostrar los proyectos de acuerdo al usuario logueado
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
    Clase encargada de mostrar los detalles de una view
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
    Clase encargada de mostrar los miembros de un proyecto
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
    Clase encargada de manejar la creacion de un proyecto
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

class ProjectDeleteView(ProjectPermissionMixin, ProjectStatusMixin, View):
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
            ProjectUseCase.add_member(project_id=project_id, **cleaned_data)
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

#User Story
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
        data['columns'] = ",".join(data.get('columns'))
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

        form = FormCreateUserStory(project_id, request.POST)
        if has_perm or has_role_SM:
            form = FormCreateUserStory(project_id, request.POST)
        elif (has_role_PO):
            form = FormCreateUserStoryPO(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            if not ('technical_priority' in cleaned_data):
                cleaned_data['technical_priority'] = 0
            if not ('estimation_time' in cleaned_data):
                cleaned_data['estimation_time'] = 0

            code = Project.objects.get(id=project_id).prefix + "-" + str(ProjectUseCase.count_user_stories_by_project(project_id) + 1)
            ProjectUseCase.create_user_story(code, project_id=project_id, **cleaned_data)
            messages.success(request, f"Historia de usuario <strong>{cleaned_data['title']}</strong> creado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/backlog")

        return render(request, 'backlog/create.html', {'form': form})

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
        """Use this to add extra context."""
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

class ProductBacklogEditView(CustomLoginMixin, ProjectPermissionMixin, ProjectStatusMixin, View):
    """
    Clase encargada de editar us en el product Backlog de un proyecto
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master']

    def get(self, request, project_id, us_id):
        user_story = ProjectUseCase.get_user_story_by_id(id=us_id)
        data=user_story.__dict__
        print (data)
        data['us_type']=user_story.us_type
        form = FormEditUserStory(project_id,initial=data)
        context= {
            "form" : form,
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        return render(request, 'backlog/edit.html', context)

    def post(self, request, project_id, us_id):

        form = FormEditUserStory(project_id,request.POST)
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
    Clase encargada de editar los tipos de us
    """

    def put(self, request, project_id, us_id):
        data = json.loads(request.body)
        old_us = ProjectUseCase.get_user_story_by_id(id=us_id)
        new_us =ProjectUseCase.edit_user_story(us_id, **data)
        UserStoriesUseCase.create_user_story_history(old_us, new_us, request.user, project_id)
        user_story = model_to_dict(new_us)
        return JsonResponse({"data": user_story}, status=200)
