from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .manager import CustomUserManager


class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    role_system = models.CharField(max_length=50, null=True)
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
        return self.is_admin() or self.role_system == 'user'

    class Meta:
        db_table = 'sga_user'
