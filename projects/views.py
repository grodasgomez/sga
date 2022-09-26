from django.views.generic import ListView, FormView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib import messages
from django.views import View
from django.db.models.query import QuerySet
from django.urls import reverse
#todo arreglar imports
from projects.forms import (FormCreateProject, FormCreateProjectMember, FormEditProjectMember, FormCreateUserStoryType, FormEditUserStoryType,
    FormCreateRole, ImportUserStoryTypeForm1, ImportUserStoryTypeForm2, FormCreateUserStory,FormEditUserStoryType, FormCreateRole, ImportUserStoryTypeForm1, ImportUserStoryTypeForm2,ImportRoleForm1,ImportRoleForm2, FormCreateUserStoryPO)
from projects.models import Project, UserStoryType, ProjectStatus
from projects.usecase import ProjectUseCase, RoleUseCase
from projects.models import ProjectMember
from projects.mixin import ProjectPermissionMixin
from users.models import CustomUser
from user_stories.models import UserStory

# Create your views here.
class ProjectListView(LoginRequiredMixin, View):
    """
    Clase para mostrar los proyectos de acuerdo al usuario logueado
    """
    def get(self, request):
        user: CustomUser = request.user
        if not user.is_user():
            messages.warning(request, "No eres un usuario verificado")
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
    """
    Clase encargada de mostrar los detalles de una view
    """
    def get(self, request, project_id):
        user: CustomUser = request.user
        if not user.is_user():
            messages.warning(request, "No eres un usuario verificado")
            return HttpResponseRedirect('/')
        data: Project = Project.objects.get(id=project_id)
        members: QuerySet = data.project_members.all()
        if user not in members:
            messages.warning(request, "No eres miembro")
            return HttpResponseRedirect('/projects')

        can_start_project = ProjectUseCase.can_start_project(user.id ,project_id)
        context= {
            "object" : data,
            "members" : members,
            "can_start_project" : can_start_project
        }
        return render(request, 'projects/project_detail.html', context)

    def post(self, request, project_id):
        ProjectUseCase.start_project(project_id)
        messages.success(request, 'Proyecto iniciado correctamente')
        return redirect(request.META['HTTP_REFERER'])

class ProjectMembersView(LoginRequiredMixin, View):
    """
    Clase encargada de mostrar los miembros de un proyecto
    """
    def get(self, request, project_id):
        user: CustomUser = request.user
        if not user.is_user():
            messages.warning(request, "No eres un usuario verificado")
            return HttpResponseRedirect('/')
        data: Project = Project.objects.get(id=project_id)
        members: QuerySet = data.project_members.all()
        if user not in members:
            messages.warning(request, "No eres miembro")
            return HttpResponseRedirect('/projects')
        context= {
            "members" : [],
            "project_id" : project_id,
        }
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


class ProjectMemberCreateView(ProjectPermissionMixin, View):
    """
    Clase encargada de manejar la asignacion de miembros a un proyecto
    """
    form_class = FormCreateProjectMember

    permissions = ['ABM Miembros']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = self.form_class(project_id=project_id)
        return render(request, 'project_member/create.html', {'form': form})

    def post(self, request, project_id):
        form = self.form_class(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.add_member(project_id=project_id, **cleaned_data)
            messages.success(request, f"Miembro agregado correctamente")
            return HttpResponseRedirect('/projects')
        return render(request, 'project_member/create.html', {'form': form})

class ProjectRoleCreateView(ProjectPermissionMixin, View):
    """
    Clase encargada de manejar la creacion de roles
    """
    form_class = FormCreateRole
    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = self.form_class(project_id)
        return render(request, 'roles/create.html', {'form': form,'project_id':project_id})

    def post(self, request, project_id):
        form=self.form_class(project_id,None,request.POST) #creamos un form con los datos cargados

        if form.is_valid(): #vemos si es valido
            cleaned_data=form.cleaned_data #tomamos los datos
            RoleUseCase.create_role(id=project_id, **cleaned_data)
            messages.success(request, 'Rol creado correctamente')
            return HttpResponseRedirect('/projects/'+str(project_id)+'/roles')
        #si el form no es valido retorna a la misma pagina
        return render(request, 'roles/create.html', {'form': form, 'project_id':project_id})

class ProjectRoleView(ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar los roles de un proyecto
    """
    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        #tomamos todos los roles del proyecto
        data = RoleUseCase.get_roles_by_project_no_default(project_id)
        context = {
            'roles': data,
            'project_id': project_id #id del proyecto para usar en el template
        }
        return render(request, 'roles/index.html', context) #le pasamos a la vista

#User Story
class UserStoryTypeCreateView(ProjectPermissionMixin, View):
    """
    Vista para crear un tipo de historia de usuario en un proyecto
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = FormCreateUserStoryType(project_id)
        return render(request, 'user_story_type/create.html', {'form': form})

    def post(self, request, project_id):
        form = FormCreateUserStoryType(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.create_user_story_type(project_id=project_id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario creado correctamente")

            return HttpResponseRedirect(f"/projects/{project_id}/user-story-type")
        return render(request, 'user_story_type/create.html', {'form': form})

class UserStoryTypeEditView(ProjectPermissionMixin, View):
    """
    Vista para editar un tipo de historia de usuario de un proyecto
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    def get(self, request, project_id, id):
        data = ProjectUseCase.get_user_story_type(id).__dict__
        data['columns'] = ",".join(data.get('columns'))
        form = FormEditUserStoryType(id, project_id, initial=data)
        return render(request, 'user_story_type/edit.html', {'form': form})

    def post(self, request, project_id, id):
        form = FormEditUserStoryType(id, project_id,request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            ProjectUseCase.edit_user_story_type(id, **cleaned_data)
            messages.success(request, f"Tipo de historia de usuario editado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/user-story-type")

        return render(request, 'user_story_type/edit.html', {'form': form})

class UserStoryTypeListView(ProjectPermissionMixin, ListView):
    """
    Vista que lista tipos de historias de usuario de un projecto
    """
    permissions = ['ABM Tipo US']
    roles = ['Scrum Master', 'Product Owner']

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
        return context

class ProjectRoleEditView(ProjectPermissionMixin, View):
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
            'project_id':project_id
        }
        return render(request, 'roles/edit.html', context)

    def post(self, request, project_id, role_id):
        form = FormCreateRole(project_id,role_id,request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            RoleUseCase.edit_role(role_id, **cleaned_data)
            messages.success(request, f"Rol editado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/roles")

        return render(request, 'roles/edit.html', {'form': form, 'project_id':project_id, 'role_id':role_id})

class ProjectRoleDeleteView(ProjectPermissionMixin, View):
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
            'role_id':role_id,
            'project_id':project_id
        }
        return render(request, 'roles/delete.html', context)

    def post(self, request, project_id, role_id):
        RoleUseCase.delete_role(role_id)
        messages.success(request, f"Rol borrado correctamente")
        return HttpResponseRedirect(f"/projects/{project_id}/roles")

class ProjectMemberEditView(ProjectPermissionMixin, View):
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
        print(data)
        form = FormEditProjectMember(project_id,initial=data)
        context= {
            "form" : form,
            'member_id':member_id,
            'project_id':project_id
        }
        return render(request, 'projects/project_member_edit.html', context)

    def post(self, request, project_id, member_id):
        form = FormEditProjectMember(project_id,request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            RoleUseCase.edit_project_member(member_id,project_id, **cleaned_data)
            messages.success(request, f"Miembro editado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/members")

        return render(request, 'projects/project_member_edit.html', {'form': form, 'project_id':project_id, 'member_id':member_id})


class ProductBacklogView(ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar el product Backlog de un proyecto
    """
    permissions = ['Ver Product Backlog']
    roles = ['Scrum Master', 'Developer', 'Product Owner']

    def get(self, request, project_id):
        user: CustomUser = request.user
        if not user.is_user():
            messages.warning(request, "No eres un usuario verificado")
            return HttpResponseRedirect('/')
        data: Project = Project.objects.get(id=project_id)
        members: QuerySet = data.project_members.all()
        if user not in members:
            messages.warning(request, "No eres miembro")
            return HttpResponseRedirect('/projects')

        user_stories = []
        us_type_filter_id = request.GET.get("type_us","")
        if us_type_filter_id != "":
            us_type_filter_id = int(us_type_filter_id)
            user_stories = ProjectUseCase.user_stories_by_project_and_us_type(project_id,us_type_filter_id)
        else:
            user_stories = ProjectUseCase.user_stories_by_project(project_id)

        user_story_types = ProjectUseCase.filter_user_story_type_by_project(project_id)
        context= {
            "us_type_filter_id" : us_type_filter_id,
            "user_stories" : user_stories,
            "project_id" : project_id,
            "user_story_types" : user_story_types
        }
        print(user_story_types)
        return render(request, 'backlog/index.html', context)

    def post(self, request, project_id):
        user_story_type_id = request.POST.get("filtro","")
        if user_story_type_id == "empty":
            return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id}))
        return redirect(reverse('projects:project-backlog', kwargs={'project_id': project_id})+'?type_us='+user_story_type_id)

class ProductBacklogCreateView(ProjectPermissionMixin, View):
    """
    Clase encargada de cargar el product Backlog de un proyecto
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master','Product Owner']

    def get(self, request, project_id):
        user = self.request.user
        has_perm = ProjectUseCase.member_has_permissions(user.id, project_id, self.permissions)
        has_role_SM = ProjectUseCase.member_has_roles(user.id, project_id, ['Scrum Master'])
        has_role_PO = ProjectUseCase.member_has_roles(user.id, project_id, ['Product Owner'])

        form = FormCreateUserStory(project_id)
        if has_perm or has_role_SM:
            form = FormCreateUserStory(project_id)
        elif (has_role_PO):
            form = FormCreateUserStoryPO(project_id)

        return render(request, 'backlog/create.html', {'form': form})

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

            code=str(project_id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project_id)+1)
            ProjectUseCase.create_user_story(code,project_id=project_id, **cleaned_data)
            messages.success(request, f"Historia de usuario creado correctamente")
            return HttpResponseRedirect(f"/projects/{project_id}/backlog")

        return render(request, 'backlog/create.html', {'form': form})

class UserStoryTypeImportView1(ProjectPermissionMixin, FormView):
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

    def get_success_url(self):
        return reverse('projects:user-story-type-import2', kwargs={'project_id': self.project_id, 'from_project_id': self.from_project_id})

class UserStoryTypeImportView2(ProjectPermissionMixin, FormView):
    """
    Clase encargada de manejar la segunda parte de la importacion de tipos de historias de usuario,
    seleccionando los tipos de historias de usuario a importar
    """

    permissions = ['ABM Tipo US']
    roles = ['Scrum Master']

    template_name = 'user_story_type/import2.html'
    form_class = ImportUserStoryTypeForm2

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['from_project_id'] = self.kwargs.get('from_project_id')
        kwargs['to_project_id'] = self.kwargs.get('project_id')
        return kwargs

    def form_valid(self, form):
        to_project_id = self.kwargs.get('project_id')
        user_story_types = form.cleaned_data['user_story_types']
        ProjectUseCase.import_user_story_types(to_project_id, user_story_types)
        messages.success(self.request, f"Tipos de Historias de Usuario importados correctamente")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:user-story-type-list', kwargs={'project_id': self.kwargs.get('project_id')})

class RoleImportView1(ProjectPermissionMixin, FormView):
    """
    Clase encargada de manejar la primera parte de la importacion de roles,
    seleccionando el proyecto de donde se importaran los roles
    """

    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id):
        form = ImportRoleForm1(project_id)
        return render(request, 'roles/import1.html', {'form': form})

    def post(self, request, project_id):
        form = ImportRoleForm1(project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            from_project_id=cleaned_data.get('project').id
            return HttpResponseRedirect(f"/projects/{project_id}/roles/import/{from_project_id}")
        return render(request, 'roles/import1.html', {'form': form})

class RoleImportView2(ProjectPermissionMixin, FormView):
    """
    Clase encargada de manejar la segunda parte de la importacion de roles,
    seleccionando los roles a importar
    """

    permissions = ['ABM Roles']
    roles = ['Scrum Master']

    def get(self, request, project_id, from_project_id):
        form = ImportRoleForm2(from_project_id)
        return render(request, 'roles/import2.html', {'form': form})

    def post(self, request, project_id, from_project_id):
        form = ImportRoleForm2(from_project_id, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            for role in cleaned_data.get('roles'):
                role.name=role.name+" (importado "+str(project_id)+")"
                RoleUseCase.create_role(project_id, role.name, role.description,role.permissions.all())
            messages.success(request, 'Rol/es importado/s correctamente')
            return HttpResponseRedirect(f"/projects/{project_id}/roles")
        return render(request, 'roles/import2.html', {'form': form})
