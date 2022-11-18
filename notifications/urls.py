from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationView.as_view(), name='index'),
    path('<int:notification_id>/mark', views.NotificationMarkView.as_view(), name='mark'),
]
