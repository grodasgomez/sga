import json
from django.db import models

from users.models import CustomUser

# Create your models here.
class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    project = models.ForeignKey('projects.Project', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name

class ProjectStatus(models.TextChoices):
    CREATED = 'CREATED', 'Creado'
    IN_PROGRESS = 'IN_PROGRESS', 'En progreso'
    CANCELLED = 'CANCELLED', 'Cancelado'
    FINISHED = 'FINISHED', 'Finalizado'

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    prefix = models.CharField(max_length=5)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(default=True, choices=ProjectStatus.choices, max_length=15)
    roles = models.ManyToOneRel(Role, on_delete=models.CASCADE, to='projects.Project', field_name='project')
    project_members = models.ManyToManyField(CustomUser, through='ProjectMember')
    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.user.email} - {self.project.name}"

class UserStoryType(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    columns = models.JSONField()

    @property
    def columns_list(self):
        return ",".join(self.columns)

    def __str__(self):
        return self.name
