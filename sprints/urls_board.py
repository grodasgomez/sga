from django.urls import path
from . import views

urlpatterns = [
    path('', views.SprintBoardView.as_view(), name='board'),
]
