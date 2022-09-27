"""sga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views
from users import views as views_users

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login, name='login'),
    path('accounts/', include('allauth.urls')),
    path('profile/', views_users.ProfileView.as_view(), name='profile'),
    path('', views.index, name='index'),

    path('projects/', include(('projects.urls', 'projects'))),
    path('users/', include(('users.urls', 'users'))),

    ### SOLO PARA LOGEAR CON USUARIOS DE PRUEBA ###
    path('accounts/login-email/', views.login_email, name='login-email'),
]
