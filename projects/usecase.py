from projects.models import Project, ProjectMember, ProjectStatus
from users.models import CustomUser
from projects.models import Role
from django.db.models import Q

class ProjectUseCase:

    @staticmethod
    def create_project(name, description, prefix, scrum_master):
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
        return project

    @staticmethod
    def get_non_members(project_id):
        return CustomUser.objects.exclude(projectmember__project_id=project_id)

    @staticmethod
    def get_members(project_id):
        return CustomUser.objects.filter(projectmember__project_id=project_id)

    @staticmethod
    def add_member(user, roles, project_id):
        project = Project.objects.get(id=project_id)
        project_member = ProjectMember.objects.create(
            project=project,
            user=user
        )
        for role in roles:
            project_member.roles.add(role)
        return project_member

class RoleUseCase:

    @staticmethod
    def create_role(id, name_role, description_role, permissions):
        existing_role=Role.objects.all().filter(name=name_role) #vemos si hay un rol en la bd con ese nombre
        if not existing_role:
            new_role= Role(name=name_role,description=description_role,project=Project.objects.get(id=id)) #creamos un rol
            new_role.save() #guardamos el rol en bd
            #veremos cada permiso
            for perm in permissions:
                #tomamos de la bd cada permiso con el id correspondiente
                #agregamos el permiso al rol nuevo
                new_role.permissions.add(perm)
            return True #se guardo un rol
        return False #el rol ya existe

    @classmethod
    def get_scrum_role(self):
        return self.get_role_by_name('Scrum Master')

    @classmethod
    def get_role_by_name(self, name):
        return Role.objects.get(name=name)

    @classmethod
    def get_roles_by_project(self, project_id):
        """
        Retorna los roles de un proyecto y los roles por defecto
        """
        return Role.objects.filter(Q(project_id=project_id) | Q(project_id=None))