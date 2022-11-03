from django.db.models import Q
from users.models import CustomUser
from user_stories.models import UserStory, UserStoryHistory, UserStoryComment, UserStoryTask
from projects.usecase import ProjectUseCase, RoleUseCase
from sprints.models import Sprint, SprintMember

class UserStoriesUseCase:
    @staticmethod
    def create_user_story_history(old_user_story, new_user_story, user, project_id):
        """
        Crea una entrada en el historial de cambios de una historia de usuario
        """
        description=""
        data={
            "code": old_user_story.code,
            "title": old_user_story.title,
            "description": old_user_story.description,
            "business_value": old_user_story.business_value,
            "technical_priority": old_user_story.technical_priority,
            "estimation_time": old_user_story.estimation_time,
            "sprint_priority": old_user_story.sprint_priority,
            "us_type": old_user_story.us_type.id,
            "column": old_user_story.column,
            "project": old_user_story.project.id,
            "sprint": 0,
            "sprint_member": 0
        }

        old_user_story_dic=vars(old_user_story)
        new_user_story_dic=vars(new_user_story)

        #si la nueva historia de usuario no pertenece a un sprint
        if not new_user_story.sprint:
            new_user_story_dic["sprint_id"]=0
        #si la nueva historia de usuario no tiene un miembro asignado
        if not new_user_story.sprint_member:
            new_user_story_dic["sprint_member_id"]=0
        #si la vieja historia de usuario no pertenece a un proyecto
        if old_user_story.sprint:
            data["sprint"]=old_user_story.sprint.id
        else:
            old_user_story_dic["sprint_id"]=0
        #si la vieja historia de usuario no tiene un miembro asignado
        if old_user_story.sprint_member:
            data["sprint_member"]=old_user_story.sprint_member.id
        else:
            old_user_story_dic["sprint_member_id"]=0

        keys=["title", "description", "business_value", "technical_priority", "estimation_time", "column", "sprint_id", "sprint_member_id"]
        keys_esp={
            "title": "Título", "description": "Descripción", "business_value": "Valor de negocio",
            "technical_priority": "Prioridad técnica", "column": "Columna","estimation_time": "Tiempo de estimación",
            "sprint_id": "Sprint", "sprint_member_id": "Miembro del sprint"}

        for key in old_user_story_dic:
            if key in keys:
                if old_user_story_dic[key]!=new_user_story_dic[key]:
                    description=description+keys_esp[key]+","

        if description!="":
            description=description[:-1]
            return UserStoryHistory.objects.create(user_story=new_user_story, project_member=RoleUseCase.get_project_member_by_user(user,project_id), description=description, dataJson=data)

        return None

    @staticmethod
    def user_story_history_by_us_id(user_story_id):
        """
        Retorna el historial de cambios de una historia de usuario
        """
        return UserStoryHistory.objects.filter(user_story_id=user_story_id).order_by('-created_at')

    @staticmethod
    def user_story_history_by_id(user_story_history_id):
        """
        Retorna una version de historia de usuario
        """
        return UserStoryHistory.objects.get(id=user_story_history_id)

    @staticmethod
    def restore_user_story(id, code=None, title=None, description=None, business_value=None,technical_priority=None,estimation_time=None,sprint_priority=None,us_type=None, column=None,project=None, sprint=None, sprint_member=None):
        """
        restaura una version de una us
        """
        data = {}
        if description:
            data['description'] = description
        if business_value:
            data['business_value'] = business_value
        if technical_priority:
            data['technical_priority'] = technical_priority
        if business_value or technical_priority:
            data['sprint_priority'] = round(0.6 * business_value + 0.4 * technical_priority)
        if estimation_time:
            data['estimation_time'] = estimation_time
        if sprint_priority:
            data['sprint_priority'] = sprint_priority
        if us_type:
            data['us_type'] = us_type

        data['column'] = column
        data['sprint'] = sprint
        data['sprint_member'] = sprint_member

        if sprint:
            sprint_status=sprint.status
            if sprint_status=="CANCELLED" or sprint_status=="FINISHED":
                data['column'] = 0
                data['sprint'] = None
                data['sprint_member'] = None

        UserStory.objects.filter(pk=id).update(**data)
        return UserStory.objects.get(pk=id)

    @staticmethod
    def user_story_comments_by_us_id(user_story_id):
        """
        Retorna los comentarios de una historia de usuario
        """
        return UserStoryComment.objects.filter(user_story_id=user_story_id).order_by('-created_at')

    def create_user_story_comment(us_id, user, project_id, comment):
        """
        Crea un comentario de una historia de usuario
        """
        return UserStoryComment.objects.create(user_story_id=us_id, project_member=RoleUseCase.get_project_member_by_user(user,project_id), comment=comment)

    @staticmethod
    def user_story_tasks_by_us_id(user_story_id):
        """
        Retorna las tareas de una historia de usuario
        """
        return UserStoryTask.objects.filter(user_story_id=user_story_id).order_by('-created_at')

    def create_user_story_task(user_story, user, description, hours):
        """
        Crea una tarea de una historia de usuario
        """
        sprint=user_story.sprint
        return UserStoryTask.objects.create(
            user_story=user_story,
            sprint=sprint,
            sprint_member=SprintMember.objects.get(user=user,sprint=sprint),
            description=description,
            hours_worked=hours,
            column=user_story.column #TODO esta bien?
        )

    @staticmethod
    def delete_user_story_comment(id):
        """
        Elimina un comentario
        """
        comment = UserStoryComment.objects.get(id=id)
        comment.delete()
        return comment
