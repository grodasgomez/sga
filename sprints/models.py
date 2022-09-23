import json
from django.db import models

from users.models import CustomUser

class SprintStatus(models.TextChoices):
    CREATED = 'PLANNED', 'Planeado'
    IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
    CANCELLED = 'CANCELLED', 'Cancelado'
    FINISHED = 'FINISHED', 'Finalizado'

class Sprint(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    status = models.CharField(choices=SprintStatus.choices, max_length=15, verbose_name='Estado')
    number = models.CharField(max_length=100)
    capacity = models.IntegerField(verbose_name='Capacidad en horas')
    duration = models.IntegerField(verbose_name='Duración en días')
    start_date = models.DateField(null=True, verbose_name='Fecha de inicio')
    end_date = models.DateField(null=True, verbose_name='Fecha de finalización')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"Sprint {self.number} - {self.project.name}"
