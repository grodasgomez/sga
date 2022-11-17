from .models import Notification


class NotificationUseCase:

    @staticmethod
    def get_unread_notifications(user):
        """
        Obtiene las notificaciones no leidas del usuario
        """
        notifications = Notification.objects.filter(user=user, read=False)
        return notifications

    @staticmethod
    def mark_notifications_as_read(notification_id):
        """
        Marca una notificacion como leida
        """
        notification = Notification.objects.get(id=notification_id)
        notification.read = True
        notification.save()
        return notification
