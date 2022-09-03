from users.models import Role


class RoleUseCase:

    @classmethod
    def get_scrum_role(self):
        return self.get_role_by_name('scrum master')

    @classmethod
    def get_role_by_name(self, name):
        return Role.objects.get(name=name)