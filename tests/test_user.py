from django.test import TestCase
from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()

from users.models import CustomUser

class TestUser(TestCase):
    """
    Clase para probar el modelo de usuario
    """
    def test_is_not_user(self):
        user = CustomUser()
        user.role_system = ""
        self.assertNotEqual(user.is_user(), True, "User is user")

    def test_is_user(self):
        user = CustomUser()
        user.role_system = "user"
        self.assertEqual(user.is_user(), True, "User is not user")

    def test_is_admin(self):
        user = CustomUser()
        user.role_system = "admin"
        self.assertEqual(user.is_admin(), True, "User is not admin")
