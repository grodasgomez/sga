from projects.models import Project, ProjectMember, ProjectStatus
from users.usecase import RoleUseCase

class ProjectUseCase:

    @staticmethod
    def create_project(name, description, prefix, start_date, end_date, scrum_master):
        project = Project.objects.create(
            name=name,
            description=description,
            prefix=prefix,
            start_date=start_date,
            end_date=end_date,
            status=ProjectStatus.CREATED
        )
        project_member = ProjectMember.objects.create(
            project=project,
            user=scrum_master
        )
        scrum_master_role = RoleUseCase.get_scrum_role()
        project_member.roles.add(scrum_master_role)
        return project