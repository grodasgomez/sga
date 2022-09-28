from django.urls import path
from . import views

urlpatterns = [
    path('', views.SprintListView.as_view(), name='index'),
    path('<int:sprint_id>/', views.SprintView.as_view(), name='detail'),
    path('create', views.SprintCreateView.as_view(), name='create'),
    path('<int:sprint_id>/members', views.SprintMemberListView.as_view(), name='member-list'),
    path('<int:sprint_id>/members/create', views.SprintMemberCreateView.as_view(), name='member-create'),
    path('<int:sprint_id>/members/<int:sprint_member_id>/edit', views.SprintMemberEditView.as_view(), name='member-edit'),
    path('<int:sprint_id>/start', views.SprintCreateView.as_view(), name='start'),
    path('<int:sprint_id>/backlog', views.SprintBacklogView.as_view(), name='backlog'),
    path('<int:sprint_id>/backlog/assign', views.SprintBacklogAssignView.as_view(), name='backlog-assign-us'),
    path('<int:sprint_id>/backlog/<int:user_story_id>/assign', views.SprintBacklogAssignMemberView.as_view(), name='backlog-assign-member'),
]
