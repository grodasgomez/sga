from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .manager import CustomUserManager

class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=100, verbose_name='Nombres')
    last_name = models.CharField(max_length=100, verbose_name='Apellidos')
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    role_system = models.CharField(max_length=50, null=True, verbose_name='Rol del sistema')
    sprints = models.ManyToManyField('sprints.Sprint', through='sprints.SprintMember')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.role_system == 'admin'

    def is_user(self):
        return self.role_system == 'user'

    def is_verified(self):
        return not self.role_system == None

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'sga_user'
        ordering = ['last_name']
