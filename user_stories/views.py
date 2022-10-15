from django.shortcuts import render
from django.views import View
from user_stories.models import UserStoryHistory, UserStory
from user_stories.usecase import UserStoriesUseCase
from django.urls import reverse
from projects.mixin import ProjectPermissionMixin, ProjectAccessMixin
from sga.mixin import CustomLoginMixin

# Create your views here.

class UserStoryHistoryView(CustomLoginMixin, ProjectPermissionMixin, View):
    """
    Clase encargada de mostrar los roles de un proyecto
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