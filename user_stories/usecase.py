from django.db.models import Q
from users.models import CustomUser
from user_stories.models import UserStory, UserStoryHistory
from projects.usecase import ProjectUseCase, RoleUseCase


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
            "us_type": old_user_story.us_type.id,
            "column": old_user_story.column,
            "project": old_user_story.project.id,
            "sprint": 0,
            "sprint_member": 0
            }

        if old_user_story.sprint:
            data["sprint"]=old_user_story.sprint.id
        if old_user_story.sprint_member:
            data["sprint_member"]=old_user_story.sprint_member.id

        keys=["title", "description", "business_value", "technical_priority", "estimation_time", "column", "sprint", "sprint_member"]
        keys_esp={
            "title": "Título", "description": "Descripción", "business_value": "Valor de negocio",
            "technical_priority": "Prioridad técnica", "column": "Columna","estimation_time": "Tiempo de estimación",
            "sprint_id": "Sprint", "sprint_member_id": "Miembro del sprint"}

        old_user_story_dic=vars(old_user_story)
        new_user_story_dic=vars(new_user_story)
        for key in old_user_story_dic:
            if key in keys:
                if old_user_story_dic[key]!=new_user_story_dic[key]:
                    description=description+keys_esp[key]+","

        if description!="":
            description=description[:-1]
            return UserStoryHistory.objects.create(user_story=new_user_story, project_member=RoleUseCase.get_project_member_by_user(user,project_id), description=description, dataJson=data)

        return None

