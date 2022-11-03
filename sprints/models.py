from functools import cached_property
from django.db import models

from user_stories.models import UserStory, UserStoryTask


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

    @property
    def get_status_button(self):
        button = {}
        if self.status == SprintStatus.CREATED:
            button["icon"] = "fa-solid fa-rocket"
            button["text"] = "Iniciar Sprint"
        elif self.status == SprintStatus.IN_PROGRESS:
            button["icon"] = "fa fa-flag"
            button["text"] = "Finalizar Sprint"
        else:
            return None
        return button

    @cached_property
    def used_capacity(self):
        """
        Retorna la capacidad usada en el sprint
        @cached_property: permite que el valor se calcule una vez y se guarde en memoria
        mientras el objeto exista.
        """
        return UserStory.objects.filter(sprint_id=self.id).aggregate(
            models.Sum('estimation_time')
            )['estimation_time__sum'] or 0

    @cached_property
    def hours_worked(self):
        """
        Retorna las horas ya trabajadas en el sprint (de las tareas de las US).
        """
        return UserStory.objects.filter(sprint_id=self.id).aggregate(
            models.Sum('hours_worked')
            )['hours_worked__sum'] or 0

    def __str__(self):
        return f"Sprint {self.number} - {self.project.name}"

class SprintMember(models.Model):
    sprint = models.ForeignKey('sprints.Sprint', on_delete=models.CASCADE)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Usuario')
    workload = models.IntegerField(verbose_name='Carga horaria')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    @property
    def capacity(self):
        return self.workload * self.sprint.duration

    @cached_property
    def used_capacity(self):
        """
        Retorna la capacidad asignada al miembro del sprint.
        @cached_property: permite que el valor se calcule una vez y se guarde en memoria
        mientras el objeto exista.
        """
        return UserStory.objects.filter(sprint_member_id=self.id).aggregate(
            models.Sum('estimation_time')
            )['estimation_time__sum'] or 0

    @cached_property
    def hours_worked(self):
        """
        Retorna las horas trabajadas de un miembro del sprint.
        """
        return UserStoryTask.objects.filter(sprint_member_id=self.id).aggregate(
            models.Sum('hours_worked')
            )['hours_worked__sum'] or 0

    def to_assignable_data(self):
        return {
            'id': self.id,
            'workload': self.workload,
            'capacity': self.capacity,
            'used_capacity': self.used_capacity
        }
    def __str__(self):
        return f"{self.user.name}"
