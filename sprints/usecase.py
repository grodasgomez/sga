
from projects.models import Project
from sprints.models import Sprint, SprintStatus


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
    def exists_active_sprint(project_id):
        """
        Método para verificar si existe un sprint activo
        """
        return Sprint.objects.filter(
            project_id=project_id,
            status=SprintStatus.IN_PROGRESS,
        ).exists()