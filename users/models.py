from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .manager import CustomUserManager


class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    role_system = models.CharField(max_length=50, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()

    def __str__(self):
        return self.email
        
    def is_admin(self):
        return self.role_system == 'admin'
    class Meta:
        db_table = 'sga_user'


class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100) 

    def __str__(self):
        return self.name 

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100)
    project = models.ForeignKey('projects.Project', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name

    
