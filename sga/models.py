from django.db import models

class Invitation(models.Model):
    email = models.EmailField(primary_key=True)
    sent = models.DateTimeField(auto_now_add=True)
    used = models.DateTimeField(null=True)

    def __str__(self):
        return self.email