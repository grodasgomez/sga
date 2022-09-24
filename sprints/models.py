from django.db import models


class SprintStatus(models.TextChoices):
    CREATED = 'PLANNED', 'Planeado'
    IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
    CANCELLED = 'CANCELLED', 'Cancelado'
    FINISHED = 'FINISHED', 'Finalizado'

class Sprint(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    status = models.CharField(choices=SprintStatus.choices, max_length=15, verbose_name='Estado')
    number = models.IntegerField()
    capacity = models.IntegerField(null=True, verbose_name='Capacidad en horas')
    duration = models.IntegerField(null=True, verbose_name='Duración en días')
    start_date = models.DateField(null=True, verbose_name='Fecha de inicio')
    end_date = models.DateField(null=True, verbose_name='Fecha de finalización')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    @property
    def name(self):
        return f"Sprint {self.number}"

    def __str__(self):
        return f"Sprint {self.number} - {self.project.name}"

class SprintMember(models.Model):
    sprint = models.ForeignKey('sprints.Sprint', on_delete=models.CASCADE)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Usuario')
    workload = models.IntegerField(verbose_name='Carga horaria')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user.name}"
