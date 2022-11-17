from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from .usecase import NotificationUseCase

from sga.mixin import CustomLoginMixin

# Create your views here.


class NotificationView(CustomLoginMixin, View):
    """
    Vista para visualizar notificaciones del usuario logueado
    """
    template_name = 'notifications.html'

    def get(self, request):
        notifications = NotificationUseCase.get_unread_notifications(
            request.user)
        context = {
            'notifications': notifications
        }
        return render(request, self.template_name, context)


class NotificationMarkView(CustomLoginMixin, View):
    """
    Vista para marcar una notification como leida
    """
    template_name = 'notifications.html'

    def get(self, request, notification_id):
        NotificationUseCase.mark_notifications_as_read(notification_id)
        return redirect(reverse("notifications:index"))
