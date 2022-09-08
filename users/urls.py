
from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views
from users import views as views_users

urlpatterns = [
    #TODO listar usuarios luego debe estar en otro lado
    path('', views.UsersView.as_view(), name='index'),
]