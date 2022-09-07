from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('<int:pk>/', views.ProjectView.as_view(), name='project-detail'),
    path('create', views.ProjectCreateView.as_view(), name='create'),
    path('<int:id>/members/create', views.ProjectMemberCreateView.as_view(), name='create-member'),
    path('<int:id>/roles/create', views.ProjectRoleCreaterView.as_view(), name='create-role'), #esto debe arreglar ale
    path('<int:id>/roles', views.ProjectRoleView.as_view(), name='index-roles'), #el index de roles dedl proyecto, el id es del proyecto
]
