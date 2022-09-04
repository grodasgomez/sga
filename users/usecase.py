from users.models import Role
from django.db.models import Q


class RoleUseCase:

    @classmethod
    def get_scrum_role(self):
        return self.get_role_by_name('scrum master')

    @classmethod
    def get_role_by_name(self, name):
        return Role.objects.get(name=name)

    @classmethod
    def get_roles_by_project(self, project_id):
        """
        Retorna los roles de un proyecto y los roles por defecto
        """
        return Role.objects.filter(Q(project_id=project_id) | Q(project_id=None))