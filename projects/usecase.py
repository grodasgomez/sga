from django.db.models import Q
from datetime import date

from projects.models import Project, ProjectMember, ProjectStatus
from projects.models import Role, UserStoryType
from users.models import CustomUser

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


class RoleUseCase:
    @staticmethod
    def create_role(id, name, description, permissions):
        """
        Crea un rol y lo guarda en la base de datos
        """
        existing_role=Role.objects.all().filter(name=name) #vemos si hay un rol en la bd con ese nombre

        new_role= Role(name=name,description=description,project=Project.objects.get(id=id)) #creamos un rol
        new_role.save() #guardamos el rol en bd
        #veremos cada permiso
        for perm in permissions:
            #tomamos de la bd cada permiso con el id correspondiente
            #agregamos el permiso al rol nuevo
            new_role.permissions.add(perm)

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
