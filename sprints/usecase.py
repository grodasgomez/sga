
from projects.models import Project, ProjectMember
from sprints.models import Sprint, SprintMember, SprintStatus
from django.db.models.query import QuerySet

from users.models import CustomUser


class SprintUseCase:

    @staticmethod
    def create_sprint(project_id):
        """
        Método para crear un nuevo sprint
        """
        # Obtenemos el proyecto
        project = Project.objects.get(id=project_id)

        # Obtenemos el último sprint
        last_sprint = SprintUseCase.get_last_sprint(project_id)

        # Creamos el nuevo sprint
        sprint = Sprint.objects.create(
            project=project,
            status=SprintStatus.CREATED,
            capacity=0,
            number=last_sprint.number + 1 if last_sprint else 1,
        )

        return sprint

    @staticmethod
    def get_last_sprint(project_id):
        """
        Método para obtener el último sprint de un proyecto
        """
        return Sprint.objects.filter(project_id=project_id).last()

    @staticmethod
    def exists_created_sprint(project_id):
        return Sprint.objects.filter(project_id=project_id, status=SprintStatus.CREATED).exists()

    @staticmethod
    def exists_active_sprint(project_id):
        """
        Método para verificar si existe un sprint activo
        """
        return Sprint.objects.filter(
            project_id=project_id,
            status=SprintStatus.IN_PROGRESS,
        ).exists()

    @staticmethod
    def get_addable_users(project_id, sprint_id):
        """
        Método para obtener los usuarios que pueden ser agregados a un sprint
        """
        user_ids = ProjectMember.objects.filter(
            project_id=project_id,
        ).exclude(
            roles__name__in=['Scrum Master', 'Product Owner']
        ).exclude(
            user__sprints__id=sprint_id
        ).values_list('user', flat=True)
        users = CustomUser.objects.filter(id__in=user_ids)
        print(users)
        return users
    @staticmethod
    def get_sprint_members(sprint_id):
        """
        Método para obtener los usuarios que pueden ser agregados a un sprint
        """
        return SprintMember.objects.filter(sprint_id=sprint_id)

    @staticmethod
    def add_sprint_member(user, sprint_id, workload):
        """
        Método para agregar un miembro a un sprint
        """
        sprint: Sprint = Sprint.objects.get(id=sprint_id)
        sprint_member = SprintMember.objects.create(
            user=user,
            sprint=sprint,
            workload=workload,
        )
        # Aumentar la capacidad del sprint
        sprint.capacity += workload
        sprint.save()
        return sprint_member