from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.UserStoryHistoryView.as_view(), name='index'),
    path('<int:user_story_history_id>/', views.UserStoryHistoryRestoreView.as_view(), name='restore'),
]