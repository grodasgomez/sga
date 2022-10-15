from django.urls import path, include
from . import views

urlpatterns = [
    path('<int:project_id>/backlog/<int:user_story_id>/history/', views.UserStoryHistoryView.as_view(), name='user-story-history'),
]