from django.test import TestCase
from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()

from users.models import CustomUser
from users.usecase import UserUseCase

class TestUser(TestCase):
    """
    Clase para probar el modelo de usuario
    """
    def test_is_not_user(self):
        user = CustomUser()
        user.role_system = ""
        self.assertNotEqual(user.is_user(), True, "User es user")

    def test_is_user(self):
        user = CustomUser()
        user.role_system = "user"
        self.assertEqual(user.is_user(), True, "User no es user")

    def test_is_not_admin(self):
        user = CustomUser()
        user.role_system = ""
        self.assertNotEqual(user.is_admin(), True, "User es admin")

    def test_is_admin(self):
        user = CustomUser()
        user.role_system = "admin"
        self.assertEqual(user.is_admin(), True, "User no es admin")

    def test_update_system_role(self):
        '''
        Prueba para actualizar el rol del sistema
        '''
        user1 = CustomUser()
        user1.role_system = "user"
        user1.email = "user1@gmail.com"
        user1.save()
        user2 = CustomUser()
        user2.role_system = "admin"
        user2.email = "user2@gmail.com"
        user2.save()
        user1 = UserUseCase.update_system_role(user1.id, "admin")
        user2 = UserUseCase.update_system_role(user2.id, "user")
        self.assertEqual(user1.role_system, "admin", "Actualización de rol fallida")
        self.assertEqual(user2.role_system, "user", "Actualización de rol fallida")
