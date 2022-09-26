from projects.models import Project, ProjectMember
from sprints.models import Sprint, SprintMember, SprintStatus
from projects.usecase import ProjectUseCase
from users.models import CustomUser
from user_stories.models import UserStory

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
        return users

    @staticmethod
    def get_sprint_members(sprint_id):
        """
        Método para obtener los sprint_members que estan en un sprint
        """
        return SprintMember.objects.filter(sprint_id=sprint_id)

    @staticmethod
    def get_assignable_sprint_members(sprint_id):
        """
        Método para obtener los sprint members que pueden ser asignados a una historia de usuario
        """
        return SprintUseCase.get_sprint_members(sprint_id)

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

    @staticmethod
    def edit_sprint_member(sprint_member_id, workload):
        """
        Método para editar la carga horaria de un miembro de un sprint
        """
        sprint_member = SprintMember.objects.get(id=sprint_member_id)
        sprint = sprint_member.sprint

        # Actualizar la capacidad del sprint
        sprint.capacity -= sprint_member.workload
        sprint.capacity += workload
        sprint.save()

        # Actualizar la carga horaria del miembro
        sprint_member.workload = workload
        sprint_member.save()

        return sprint_member

    @staticmethod
    def assign_us_sprint(sprint_id, user_story_id):
        """
        Asigna una historia de usuario a un sprint
        """
        data = {
            'sprint': sprint_id
        }
        return UserStory.objects.filter(id=user_story_id).update(**data)

    @staticmethod #todo, verificacion, esta bien esto?
    def assign_us_sprint_member(sprint_member, user_story_id):
        """
        Asigna una historia de usuario a un miembro de un sprint
        """
        data = {}
        if not sprint_member:
            data = {
                'sprint_member': None
            }
        else:
            data = {
                'sprint_member': sprint_member
            }
        return UserStory.objects.filter(id=user_story_id).update(**data)

    @staticmethod
    def user_stories_by_sprint(sprint_id):
        """
        Retorna las historias de usuario de un Sprint
        """
        return UserStory.objects.filter(sprint_id=sprint_id)

    @staticmethod
    def assignable_us_to_sprint(project_id, sprint_id):
        """
        Retorna las historias de usuario de un Sprint
        """
        return ProjectUseCase.user_stories_by_project(project_id).exclude(sprint=sprint_id)
