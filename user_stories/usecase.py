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

        print (description)
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

