from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('<int:id>/', views.ProjectView.as_view(), name='project-detail'),
    path('create', views.ProjectCreateView.as_view(), name='create'),
    path('<int:id>/members/create', views.ProjectMemberCreateView.as_view(), name='create-member'),

    #User story type
    path('<int:project_id>/user-story-type/', views.UserStoryTypeListView.as_view(), name='user-story-type-list'),
    path('<int:project_id>/user-story-type/create', views.UserStoryTypeCreateView.as_view(), name='user-story-type-create'),
    path('<int:project_id>/user-story-type/<int:id>/edit', views.UserStoryTypeEditView.as_view(), name='user-story-type-edit'),
]
