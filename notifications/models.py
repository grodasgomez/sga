from django.db import models

class Notification(models.Model):
    """
    Modelo para notificaciones. Las notificaciones son mensajes para informar al usuario de algún evento.
    """
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
