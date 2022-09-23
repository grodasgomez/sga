from django.urls import path
from . import views

urlpatterns = [
    path('', views.SprintListView.as_view(), name='index'),
    path('<int:pk>/', views.SprintView.as_view(), name='detail'),
    path('create', views.SprintCreateView.as_view(), name='create'),
    path('<int:sprint_id>/members', views.SprintMemberListView.as_view(), name='member-list'),
    path('<int:sprint_id>/members/create', views.SprintMemberCreateView.as_view(), name='member-create'),
    path('<int:id>/start', views.SprintCreateView.as_view(), name='start'),

]
