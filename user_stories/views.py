from django.shortcuts import render
from django.views import View
from user_stories.models import UserStoryHistory, UserStory
from user_stories.usecase import UserStoriesUseCase
from django.urls import reverse
from projects.mixin import ProjectPermissionMixin, ProjectAccessMixin
from sga.mixin import CustomLoginMixin
import json
from projects.forms import FormEditUserStory

# Create your views here.

class UserStoryHistoryView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar el historial de cambios de una historia de usuario
    """
    permissions = ['Historial']
    roles = ['Scrum Master']

    def get(self, request, project_id, user_story_id):
        #tomamos las viejas versiones de una historia de usuario
        data = UserStoriesUseCase.user_story_history_by_us_id(user_story_id)
        context = {
            'us_history': data,
            'project_id': project_id, #id del proyecto para usar en el template
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        return render(request, 'history/index.html', context) #le pasamos a la vista

class UserStoryHistoryRestoreView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de restaurar una version vieja de una historia de usuario
    """
    permissions = ['Historial']
    roles = ['Scrum Master']

    def get(self, request, project_id, user_story_id):
        user_story = UserStoriesUseCase.user_story_history_by_us_id(user_story_id)
        data=json.loads(user_story.dataJson)
        form = FormEditUserStory(project_id,initial=data)
        context= {
            "form" : form,
            "backpage": reverse("projects:project-backlog", kwargs={"project_id": project_id})
        }
        return render(request, 'backlog/edit.html', context)