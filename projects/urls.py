from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:project_id>/', views.ProjectView.as_view(), name='project-detail'),
    path('<int:project_id>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    path('<int:project_id>/members/create/', views.ProjectMemberCreateView.as_view(), name='create-member'),
    path('<int:project_id>/members/', views.ProjectMembersView.as_view(), name='project-members'),
    path('<int:project_id>/members/<int:member_id>/edit/', views.ProjectMemberEditView.as_view(), name='project-member-edit'),
    path('<int:project_id>/backlog/', views.ProductBacklogView.as_view(), name='project-backlog'),
    path('<int:project_id>/backlog/create/', views.ProductBacklogCreateView.as_view(), name='project-backlog-create'),
    path('<int:project_id>/backlog/<int:us_id>/edit/', views.ProductBacklogEditView.as_view(), name='project-backlog-edit'),
    path('<int:project_id>/backlog/<int:us_id>/', views.ProductBacklogDetailView.as_view(), name='project-backlog-detail'),
    path('<int:project_id>/backlog/<int:us_id>/comments/create', views.ProductBacklogCreateCommentView.as_view(), name='comment-create'),
    path('<int:project_id>/backlog/<int:us_id>/tasks/create', views.ProductBacklogCreateTaskView.as_view(), name='task-create'),
    path('<int:project_id>/backlog/<int:us_id>/comments/<int:comment_id>/delete', views.ProductBacklogDeleteCommentView.as_view(), name='comment-delete'),
    path('<int:project_id>/velocity', views.VelocityChartView.as_view(), name='velocity'),

    #Attachments
    path('<int:project_id>/backlog/<int:us_id>/attachments/<int:attachment_id>', views.UserStoryAttachmentDownloadView.as_view(), name='us-attachment-download'),
    path('<int:project_id>/backlog/<int:us_id>/attachments/create', views.UserStoryAttachmentCreateView.as_view(), name='us-attachment-create'),
    path('<int:project_id>/backlog/<int:us_id>/attachments/<int:attachment_id>/delete', views.UserStoryAttachmentDeleteView.as_view(), name='us-attachment-delete'),

    #User story type
    path('<int:project_id>/user-story-type/', views.UserStoryTypeListView.as_view(), name='user-story-type-list'),
    path('<int:project_id>/user-story-type/create/', views.UserStoryTypeCreateView.as_view(), name='user-story-type-create'),
    path('<int:project_id>/user-story-type/<int:id>/edit/', views.UserStoryTypeEditView.as_view(), name='user-story-type-edit'),
    path('<int:project_id>/user-story-type/import/', views.UserStoryTypeImportView1.as_view(), name='user-story-type-import1'),
    path('<int:project_id>/user-story-type/import/<int:from_project_id>/', views.UserStoryTypeImportView2.as_view(), name='user-story-type-import2'),

    #Role
    path('<int:project_id>/roles/create/', views.ProjectRoleCreateView.as_view(), name='create-role'), #esto debe arreglar ale
    path('<int:project_id>/roles/', views.ProjectRoleView.as_view(), name='index-roles'), #el index de roles dedl proyecto, el id es del proyecto
    path('<int:project_id>/roles/<int:role_id>/edit/', views.ProjectRoleEditView.as_view(), name='edit-role'), #esto debe arreglar ale
    path('<int:project_id>/roles/<int:role_id>/delete/', views.ProjectRoleDeleteView.as_view(), name='delete-role'),
    path('<int:project_id>/roles/import/', views.RoleImportView1.as_view(), name='import-role1'),
    path('<int:project_id>/roles/import/<int:from_project_id>/', views.RoleImportView2.as_view(), name='import-role2'),

    #Sprint
    path('<int:project_id>/sprints/', include(('sprints.urls', 'sprints'))),

    # Active board
    path('<int:project_id>/board/', include(('sprints.urls_board', 'board'))),

    # API
    path('<int:project_id>/user-stories/<int:us_id>/', views.UserStoryEditApiView.as_view()),

    # User Stories
    path('<int:project_id>/backlog/<int:user_story_id>/history/', include(('user_stories.urls', 'history'))),

    # Holidays
    path('<int:project_id>/holidays/', views.ProjectHolidayView.as_view(), name='index-holidays'), #el index de feriados del proyecto, el id es del proyecto
    path('<int:project_id>/holidays/create/', views.ProjectCreateHolidayView.as_view(), name='create-holiday'), #el index de feriados del proyecto, el id es del proyecto
    path('<int:project_id>/holidays/delete/<int:project_holiday_id>/', views.ProjectDeleteHolidayView.as_view(), name='delete-holiday'), #el index de feriados del proyecto, el id es del proyecto
]
