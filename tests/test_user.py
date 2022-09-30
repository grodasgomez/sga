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

    def test_users_by_filter(self):
        '''
        Prueba para buscar usuarios por nombre, apellido, correo o rol de sistema
        '''
        user1 = CustomUser()
        user1.first_name = "name1"
        user1.last_name = "lastname1"
        user1.email = "1@gmail.com"
        user1.role_system = "user"
        user1.save()
        user2 = CustomUser()
        user2.first_name = "name2"
        user2.last_name = "lastname2"
        user2.email = "2@gmail.com"
        user2.role_system = "admin"
        user2.save()

        found_users = UserUseCase.users_by_filter("name1")
        self.assertEqual(len(found_users), 1, "No se encontró el usuario")

        found_users = UserUseCase.users_by_filter("lastname2")
        self.assertEqual(len(found_users), 1, "No se encontró el usuario")

        found_users = UserUseCase.users_by_filter("1@gmail.com")
        self.assertEqual(len(found_users), 1, "No se encontró el usuario")

        found_users = UserUseCase.users_by_filter("user")
        self.assertEqual(len(found_users), 1, "No se encontró el usuario")

        #deberia traer 2
        found_users = UserUseCase.users_by_filter("name")
        self.assertEqual(len(found_users), 2, "No se encontraron los usuarios")
