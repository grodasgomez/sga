from django.shortcuts import render, redirect
from django.views import View
from user_stories.models import UserStoryHistory, UserStory
from user_stories.usecase import UserStoriesUseCase
from projects.usecase import ProjectUseCase
from sprints.usecase import SprintUseCase
from django.urls import reverse
from projects.mixin import ProjectPermissionMixin, ProjectAccessMixin
from sga.mixin import CustomLoginMixin
import json
from projects.forms import FormEditUserStory
from user_stories.forms import FormRestoreUserStoryHistory
from django.http import HttpResponseRedirect
from django.contrib import messages

class UserStoryHistoryView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar el historial de cambios de una historia de usuario
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master']

    def get(self, request, project_id, user_story_id):
        #tomamos las viejas versiones de una historia de usuario
        data = UserStoriesUseCase.user_story_history_by_us_id(user_story_id)
        context = {
            "us_history": data,
            "project_id": project_id, #id del proyecto para usar en el template
            "user_story_id" : user_story_id,
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        return render(request, 'history/index.html', context) #le pasamos a la vista

class UserStoryHistoryRestoreView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de restaurar una version vieja de una historia de usuario
    """
    permissions = ['ABM US Proyecto']
    roles = ['Scrum Master']

    def get(self, request, project_id, user_story_id, user_story_history_id):
        user_story_history = UserStoriesUseCase.user_story_history_by_id(user_story_history_id)
        data=user_story_history.dataJson
        data["us_type"]=ProjectUseCase.get_user_story_type(data["us_type"])
        if (data["sprint"]!=0):
            data["sprint"]=SprintUseCase.get_sprint_by_id(data["sprint"])
        if (data["sprint_member"]!=0):
            data["sprint_member"]=SprintUseCase.get_sprint_member_by_id(data["sprint_member"])
        form = FormRestoreUserStoryHistory(project_id,initial=data)
        context= {
            "form" : form,
            "project_id" : project_id,
            "user_story_id" : user_story_id,
            "user_story_history_id" : user_story_history_id,
            "backpage": reverse("projects:history:index", kwargs={"project_id": project_id, "user_story_id": user_story_id})
        }
        return render(request, 'history/restore.html', context)

    def post(self, request, project_id, user_story_id, user_story_history_id):
        user_story_history = UserStoriesUseCase.user_story_history_by_id(user_story_history_id)
        data=user_story_history.dataJson
        data["us_type"]=ProjectUseCase.get_user_story_type(data["us_type"])
        if (data["sprint"]!=0):
            data["sprint"]=SprintUseCase.get_sprint_by_id(data["sprint"])
        else:
            data["sprint"]=None
        if (data["sprint_member"]!=0):
            data["sprint_member"]=SprintUseCase.get_sprint_member_by_id(data["sprint_member"])
        else:
            data["sprint_member"]=None
        form=FormRestoreUserStoryHistory(project_id, initial=data)
        context= {
            "form" : form,
            "project_id" : project_id,
            "user_story_id" : user_story_id,
            "user_story_history_id" : user_story_history_id,
            "backpage": reverse("projects:history:index", kwargs={"project_id": project_id, "user_story_id": user_story_id})
        }
        old_user_story = ProjectUseCase.get_user_story_by_id(id=user_story_id)

        UserStoriesUseCase.restore_user_story(user_story_id,**data)

        new_user_story = ProjectUseCase.get_user_story_by_id(id=user_story_id)
        result=UserStoriesUseCase.create_user_story_history(old_user_story, new_user_story, request.user, project_id)

        if  (result):
            messages.success(request, f"Historia de usuario <strong>{data['title']}</strong> restaurada correctamente")
        else:
            messages.success(request, f"La Historia de usuario <strong>{data['title']}</strong> ya poseia los datos seleccionados")
        return redirect(reverse("projects:history:index", kwargs={"project_id": project_id, "user_story_id": user_story_id}))
