from django.db import models

from users.models import CustomUser, Role

# Create your models here.
class ProjectStatus(models.TextChoices):
    CREATED = 'CREATED', 'Creado'
    PENDING = 'PENDING', 'Pendiente'
    IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
    CANCELLED = 'CANCELLED', 'Cancelado'
    FINISHED = 'FINISHED', 'Finalizado'

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    prefix = models.CharField(max_length=5)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(default=True, choices=ProjectStatus.choices, max_length=15)
    roles = models.ManyToOneRel(Role, on_delete=models.CASCADE, to='projects.Project', field_name='project')

    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.ManyToManyField(Role)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.username


