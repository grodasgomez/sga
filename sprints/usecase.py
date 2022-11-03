from datetime import datetime
from projects.models import Project, ProjectMember
from sprints.models import Sprint, SprintMember, SprintStatus
from projects.usecase import ProjectUseCase
from users.models import CustomUser
from user_stories.models import UserStory, UserStoryStatus
from user_stories.usecase import UserStoriesUseCase
import copy
from datetime import timedelta

class SprintUseCase:
    @staticmethod
    def create_sprint(project_id, duration):
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
            duration=duration,
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
        users = ProjectMember.objects.filter(
            project_id=project_id,
        ).exclude(
            user__sprints__id=sprint_id
        )
        users = [ user.user.id for user in users if not (user.roles.count() == 1 and user.roles.all().first().name == 'Product Owner') ]
        users = CustomUser.objects.filter(id__in=users)
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
        member_capacity = workload * sprint.duration
        sprint.capacity += member_capacity
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
        sprint.capacity -= sprint.duration * sprint_member.workload
        sprint.capacity += sprint.duration * workload
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
        us = UserStory.objects.get(id=user_story_id)
        us.sprint = Sprint.objects.get(id=sprint_id)
        us.save()
        return us

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

    def start_sprint(sprint):
        """
        Inicia un sprint
        """
        project_has_active_sprint = SprintUseCase.exists_active_sprint(sprint.project_id)
        if project_has_active_sprint:
            raise CustomError('Ya existe un sprint activo en el proyecto')

        has_us = SprintUseCase.user_stories_by_sprint(sprint.id).exists()
        if not has_us:
            raise CustomError('No se puede iniciar un sprint sin historias de usuario asignadas')

        has_members = SprintUseCase.get_sprint_members(sprint.id).exists()
        if not has_members:
            raise CustomError('No se puede iniciar un sprint sin miembros asignados')

        sprint.status = SprintStatus.IN_PROGRESS
        sprint.start_date = datetime.now()

        aux = SprintUseCase.calculate_sprint_end_date(sprint.start_date.date(), sprint.duration, sprint.project_id)

        sprint.end_date = aux
        sprint.save()
        return sprint

    def recalculate_sprint_end_date(sprint):
        """
        Recalcula la fecha de fin de un sprint
        """
        if (sprint):
            sprint.end_date = SprintUseCase.calculate_sprint_end_date(sprint.start_date, sprint.duration, sprint.project_id)
            sprint.save()
        return sprint
    
    @staticmethod
    def calculate_sprint_end_date(start_date, duration, project_id):
        """
        Calcula la fecha de finalización de un sprint
        """
        aux= start_date
        holidays= ProjectUseCase.get_holidays_by_project(project_id=project_id)
        holidays= holidays.values_list('date', flat=True)
        cont=0
        while (True):

            if aux not in holidays and aux.weekday() < 5:
                cont=cont+1

            if cont is duration:
                break

            aux=aux+timedelta(days=1)
        
        return aux


    @staticmethod
    def finish_sprint(sprint, user, project_id):
        """
        Finaliza un sprint
        """
        sprint.status = SprintStatus.FINISHED
        sprint.end_date = datetime.now()
        sprint.save()
        user_stories = UserStory.objects.filter(sprint=sprint)
        for us in user_stories:
            #realizamos una copia de la us para el historial
            old_user_story = copy.copy(us)
            if( len(us.us_type.columns) == us.column + 1):
                us.status = UserStoryStatus.FINISHED
            else:
                us.sprint_member = None
                us.sprint = None
                us.column = 0
                us.sprint_priority = us.sprint_priority + 30
            us.save()
            UserStoriesUseCase.create_user_story_history(old_user_story, us, user, project_id)
        return sprint  

    @staticmethod
    def get_current_sprint(project_id):
        """
        Retorna el sprint activo de un proyecto
        """
        return Sprint.objects.filter(project_id=project_id, status=SprintStatus.IN_PROGRESS).first()

    @staticmethod
    def get_sprint_by_id(sprint_id):
        """
        Retorna el sprint por id
        """
        return Sprint.objects.get(id=sprint_id)

    @staticmethod
    def get_sprint_member_by_id(sprint_member_id):
        """
        Retorna el sprint member por id
        """
        return SprintMember.objects.get(id=sprint_member_id)

class CustomError(Exception):
    pass
