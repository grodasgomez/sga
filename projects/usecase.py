from django.db.models import Q
from datetime import date

from projects.models import Project, ProjectMember, ProjectStatus
from projects.models import Role, UserStoryType
from users.models import CustomUser
from user_stories.models import UserStory

class ProjectUseCase:
    @staticmethod
    def create_project(name, description, prefix, scrum_master)-> Project:
        """
        Crea un proyecto con un scrum master y un tipo de historia por defecto
        """
        project = Project.objects.create(
            name=name,
            description=description,
            prefix=prefix,
            status=ProjectStatus.CREATED
        )
        project_member = ProjectMember.objects.create(
            project=project,
            user=scrum_master
        )
        scrum_master_role = RoleUseCase.get_scrum_role()
        project_member.roles.add(scrum_master_role)

        #Creamos el tipo de historia de usuario por defecto para el proyecto
        ProjectUseCase.create_default_user_story_type(project_id=project.id)
        return project

    @staticmethod
    def start_project(project_id):
        """
        Inicia un proyecto
        """
        project = Project.objects.get(id=project_id)
        project.status = ProjectStatus.IN_PROGRESS
        project.start_date = date.today()
        project.save()

    @staticmethod
    def create_default_user_story_type(project_id):
        """
        Crea un tipo de historia de usuario por defecto para el proyecto dado
        """
        return ProjectUseCase.create_user_story_type(
            name='Historia de Usuario',
            project_id=project_id,
            columns=['Por hacer', 'En progreso', 'Hecho']
        )

    @staticmethod
    def get_non_members(project_id):
        """
        Obtener los usuarios que no son parte del proyecto, no son admin y son usuarios verificados
        """
        return CustomUser.objects.exclude(projectmember__project_id=project_id).exclude(role_system='admin').exclude(role_system=None)

    @staticmethod
    def get_members(project_id):
        """
        Obtener los usuarios que son parte del proyecto
        """
        return CustomUser.objects.filter(projectmember__project_id=project_id)

    @staticmethod
    def add_member(user, roles, project_id):
        """
        Agrega un usuario al proyecto
        """
        project = Project.objects.get(id=project_id)
        project_member = ProjectMember.objects.create(
            project=project,
            user=user
        )
        for role in roles:
            project_member.roles.add(role)
        return project_member

    @staticmethod
    def create_user_story_type(name, columns, project_id):
        """
        Crea un tipo de historia de usuario para el proyecto dado
        """
        project = Project.objects.get(id=project_id)
        return UserStoryType.objects.create(
            name=name,
            project=project,
            columns=columns
        )

    @staticmethod
    def edit_user_story_type(id, name, columns):
        """
        Edita un tipo de historia de usuario
        """
        data = {}
        if name:
            data['name'] = name
        if columns:
            data['columns'] = columns
        return UserStoryType.objects.filter(id=id).update(**data)

    @staticmethod
    def get_user_story_type(id):
        """
        Obtiene un tipo de historia de usuario
        """
        return UserStoryType.objects.get(id=id)

    @staticmethod
    def filter_user_story_type_by_project(project_id):
        """
        Obtiene los tipos de historia de usuario de un proyecto
        """
        return UserStoryType.objects.filter(project_id=project_id)

    @staticmethod
    def member_has_permissions(user_id, project_id, permissions):
        """
        Verifica si un miembro del proyecto tiene una lista de permisos
        """
        return ProjectMember.objects.filter(
           user_id=user_id,project_id=project_id, roles__permissions__name__in=permissions
        ).exists()

    @staticmethod
    def member_has_roles(user_id, project_id, roles):
        """
        Verifica si un miembro del proyecto tiene una lista de roles
        """
        return ProjectMember.objects.filter(
            user_id=user_id,project_id=project_id, roles__name__in=roles
        ).exists()

    @staticmethod
    def can_start_project(user_id, project_id):
        """
        Verifica si un miembro de proyecto puede tiene permisos para iniciar el proyecto
        """
        permissions = ['Iniciar Proyecto']
        roles = ['Scrum Master']
        tiene_permisos = ProjectUseCase.member_has_permissions(user_id, project_id, permissions)
        es_scrum_master = ProjectUseCase.member_has_roles(user_id, project_id, roles)

        return es_scrum_master or tiene_permisos

    @staticmethod
    def user_stories_by_project(project_id):
        """
        Retorna las historias de usuario de un proyecto
        """
        return UserStory.objects.filter(project_id=project_id)

    @staticmethod
    def user_stories_by_project_filter(project_id, user_story_type_id, busqueda):
        """
        Retorna las historias de usuario de un proyecto filtradas
        """
        lista = UserStory.objects.filter(project_id=project_id)

        if user_story_type_id:
            lista = lista.filter(us_type=user_story_type_id)

        return lista.filter(
            Q(title__icontains=busqueda) |
            Q(description__icontains=busqueda) |
            Q(code__icontains=busqueda) |
            Q(us_type__name__icontains=busqueda)
        )

    @staticmethod
    def count_user_stories_by_project(project_id):
        """
        cuenta las historias de usuario de un proyecto
        """
        return UserStory.objects.filter(project_id=project_id).count()

    @staticmethod
    def create_user_story(code, title, description, business_value,technical_priority,estimation_time,us_type, project_id):
        """
        Crea un us para el proyecto dado
        """
        sprint_priority = round(0.6 * business_value + 0.4 * technical_priority)
        project = Project.objects.get(id=project_id)
        return UserStory.objects.create(
            code=code,
            title=title,
            description=description,
            business_value=business_value,
            technical_priority=technical_priority,
            sprint_priority=sprint_priority,
            estimation_time=estimation_time,
            us_type=us_type,
            project=project)

    @staticmethod
    def import_user_story_types(project_id, from_project_id, user_story_types):
        """
        Importa los tipos de user story de un proyecto
        """
        from_project = Project.objects.get(id=from_project_id)
        for user_story_type in user_story_types:
            name = f"{user_story_type.name} (importado {from_project.name})"
            ProjectUseCase.create_user_story_type(
                project_id=project_id, name=name, columns=user_story_type.columns)

    def get_user_story_by_id(id):
        """
        Obtener us por id
        """
        return UserStory.objects.get(id=id)

    def edit_user_story(id, title=None, description=None, business_value=None,technical_priority=None,estimation_time=None,us_type=None, column=None):
        """
        editar una us
        """
        data = {}
        if description:
            data['description'] = description
        if business_value:
            data['business_value'] = business_value
        if technical_priority:
            data['technical_priority'] = technical_priority
        if business_value or technical_priority:
            data['sprint_priority'] = round(0.6 * business_value + 0.4 * technical_priority)
        if estimation_time:
            data['estimation_time'] = estimation_time
        if us_type:
            data['us_type'] = us_type
        # Column es None por default, puede valer 0...
        if column is not None:
            data['column'] = column

        UserStory.objects.filter(pk=id).update(**data)
        return UserStory.objects.get(pk=id)

class RoleUseCase:
    @staticmethod
    def create_role(id, name, description, permissions):
        """
        Crea un rol y lo guarda en la base de datos
        """
        new_role= Role(name=name,description=description,project=Project.objects.get(id=id)) #creamos un rol
        new_role.save() #guardamos el rol en bd
        #veremos cada permiso
        for perm in permissions:
            #tomamos de la bd cada permiso con el id correspondiente
            #agregamos el permiso al rol nuevo
            new_role.permissions.add(perm)

        return new_role

    @classmethod
    def get_scrum_role(self):
        """
        Obtiene el rol de scrum master
        """
        return self.get_role_by_name('Scrum Master')

    @classmethod
    def get_role_by_name(self, name):
        """
        Obtiene un rol por su nombre
        """
        return Role.objects.get(name=name)

    @classmethod
    def get_roles_by_project(self, project_id):
        """
        Retorna todos los roles de un proyecto
        """
        return Role.objects.filter(Q(project_id=project_id) | Q(project_id=None))

    @staticmethod
    def get_roles_by_project_no_default(project_id):
        """
        Retorna los roles custom de un proyecto
        """
        return Role.objects.filter(project_id=project_id)

    def count_roles_by_project_no_default(project_id):
        """
        Retorna los roles custom de un proyecto
        """
        return Role.objects.filter(project_id=project_id).count()

    @staticmethod
    def get_role_by_id(role_id):
        """
        Retorna un rol por su id
        """
        return Role.objects.get(id=role_id)

    @staticmethod
    def edit_role(id, name, description, permissions):
        """
        Edita un rol
        """
        role=Role.objects.get(id=id) #rol editado
        new_array_permissions=[item.id for item in permissions] #nuevos permisos seleccionados por el usuario
        original_permissions=role.permissions.all()
        original_permissions_id=[item.id for item in original_permissions] #permisos originales de la BD
        #permisos que esten entre los nuevos y no entre los originales
        to_agg=list(set(new_array_permissions) - set(original_permissions_id))
        #permisos que esten entre los originales pero no entre los nuevos
        to_remove=list(set(original_permissions_id) - set(new_array_permissions))

        for perm in permissions:
            if perm.id in to_agg:
                role.permissions.add(perm)

        for perm in original_permissions:
            if perm.id in to_remove:
                role.permissions.remove(perm)

        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        return Role.objects.filter(id=id).update(**data)

    @staticmethod
    def delete_role(id):
        """
        Borra un rol
        """
        role=Role.objects.get(id=id) #rol editado
        role.delete()
        return role

    @staticmethod
    def get_roles_from_member(member, project):
        return ProjectMember.objects.get(user=member, project=project).roles.all()

    @staticmethod
    def get_roles_from_member_id(member_id, project_id):
        project=Project.objects.get(id=project_id)
        member=project.project_members.get(id=member_id)
        return RoleUseCase.get_roles_from_member(member,project)

    def get_project_member_by_id(member_id,project_id):
        project=Project.objects.get(id=project_id)
        return project.project_members.get(id=member_id)

    @staticmethod
    def edit_project_member(id, project_id, email, roles):
        """
        Edita un miembro de un proyecto
        """
        user = RoleUseCase.get_project_member_by_id(id, project_id)
        project = Project.objects.get(id=project_id)
        member = ProjectMember.objects.get(user=user, project=project)
        new_array_roles=[item.id for item in roles] #nuevos roles seleccionados por el usuario
        original_roles=RoleUseCase.get_roles_from_member_id(id, project_id)
        original_roles_id=[item.id for item in original_roles] #roles originales de la BD
        #roles que esten entre los nuevos y no entre los originales
        to_agg=list(set(new_array_roles) - set(original_roles_id))
        #roles que esten entre los originales pero no entre los nuevos
        to_remove=list(set(original_roles_id) - set(new_array_roles))

        for role in roles:
            if role.id in to_agg:
                member.roles.add(role)

        for role in original_roles:
            if role.name != "Scrum Master":
                if role.id in to_remove:
                    member.roles.remove(role)

        return True

    def role_is_in_use(role_id):
        return ProjectMember.objects.filter(roles__id=role_id).count() > 0
