from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('create', views.ProjectCreateView.as_view(), name='create'),
    path('<int:project_id>/', views.ProjectView.as_view(), name='project-detail'),
    path('<int:project_id>/members/create', views.ProjectMemberCreateView.as_view(), name='create-member'),
    path('<int:project_id>/members', views.ProjectMembersView.as_view(), name='project-members'),
    path('<int:project_id>/members/<int:member_id>/edit', views.ProjectMemberEditView.as_view(), name='project-member-edit'),
    path('<int:project_id>/backlog', views.ProductBacklogView.as_view(), name='project-backlog'),

    #User story type
    path('<int:project_id>/user-story-type/', views.UserStoryTypeListView.as_view(), name='user-story-type-list'),
    path('<int:project_id>/user-story-type/create', views.UserStoryTypeCreateView.as_view(), name='user-story-type-create'),
    path('<int:project_id>/user-story-type/<int:id>/edit', views.UserStoryTypeEditView.as_view(), name='user-story-type-edit'),
    path('<int:project_id>/roles/create', views.ProjectRoleCreateView.as_view(), name='create-role'),
    path('<int:project_id>/roles', views.ProjectRoleView.as_view(), name='index-roles'),
    path('<int:project_id>/roles/<int:role_id>/edit', views.ProjectRoleEditView.as_view(), name='edit-role'),
    path('<int:project_id>/roles/<int:role_id>/delete', views.ProjectRoleDeleteView.as_view(), name='delete-role'),

    #Sprint
    path('<int:project_id>/sprints/', include(('sprints.urls', 'sprints'))),
]
