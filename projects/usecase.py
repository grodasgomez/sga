from projects.models import Project, ProjectMember, ProjectStatus, UserStoryType
from users.models import CustomUser
from users.usecase import RoleUseCase
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
        """
        Obtener los usuarios que no son parte del proyecto, no son admin y son usuarios verificados
        """
        return CustomUser.objects.exclude(projectmember__project_id=project_id).exclude(role_system='admin').exclude(role_system=None)

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

    @staticmethod
    def create_user_story_type(name, columns, project_id):
        project = Project.objects.get(id=project_id)
        return UserStoryType.objects.create(
            name=name,
            project=project,
            columns=columns
        )

    @staticmethod
    def edit_user_story_type(id, name, columns):
        data = {}
        if name:
            data['name'] = name
        if columns:
            data['columns'] = columns
        return UserStoryType.objects.filter(id=id).update(**data)

    @staticmethod
    def get_user_story_type(id):
        return UserStoryType.objects.get(id=id)
