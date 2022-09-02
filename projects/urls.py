from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.ProjectView.as_view(), name='index'),
    path('create', views.ProjectCreateView.as_view(), name='create'),
]
