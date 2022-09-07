from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='index'),
    path('<int:id>/', views.ProjectView.as_view(), name='project-detail'),
    path('create', views.ProjectCreateView.as_view(), name='create'),
    path('<int:id>/members/create', views.ProjectMemberCreateView.as_view(), name='create-member'),
]
