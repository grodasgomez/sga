from django.test import TestCase
from django import setup
import os
from projects.models import Permission, Project, ProjectMember, Role, UserStoryType

from projects.usecase import ProjectUseCase
from users.models import CustomUser
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()


class ProjectUseCaseTest(TestCase):
    def setUp(self):
        """
        Funcion que crea los datos iniciales en la base datos para los tests
        estos perduran durante toda la ejecucion de los tests
        """
        self.scrum_master = CustomUser.objects.create(
            first_name='Scrum',
            last_name='Master',
            email='scrum_master@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')

        self.scrum_rol = Role.objects.create(
            name='Scrum Master',
            description='Scrum Master',
        )

        self.admin = CustomUser.objects.create(
            first_name='Admin',
            last_name='Admin',
            email='admin@gmail.com',
            password='dsad',
            is_active=True,
            role_system='admin')

        self.permission = Permission.objects.create(
            name='ABM Roles',
            description='Descripcion')

        self.scrum_rol.permissions.add(self.permission)


    def test_create_project(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
        }
        project = ProjectUseCase.create_project(scrum_master=self.scrum_master,**data)
        user_story_types = UserStoryType.objects.filter(project=project)

        self.assertDictContainsSubset(data, project.__dict__, "El proyecto creado no es igual al que se creo")
        self.assertIn(self.scrum_master, project.project_members.all(), "El Scrum Master debe estar en la lista de miembros")
        self.assertEqual(len(user_story_types), 1, "No se crearon los tipos de historia de usuario por defecto")

    def test_get_non_members(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data)
        non_members = ProjectUseCase.get_non_members(project.id)
        self.assertNotIn(self.scrum_master, non_members, "El Scrum Master no debe estar en la lista de no miembros")
        self.assertNotIn(self.admin, non_members, "El Admin no debe estar en la lista de no miembros")

    def test_get_members(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data)
        members = ProjectUseCase.get_members(project.id)
        self.assertIn(self.scrum_master, members, "El Scrum Master debe estar en la lista de miembros")

    def test_add_member(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        new_member = CustomUser.objects.create(
            first_name='New',
            last_name='Member',
            email='member@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user'
        )
        roles = [self.scrum_rol]
        project = ProjectUseCase.create_project(**data)
        member = ProjectUseCase.add_member(new_member, roles, project.id)
        self.assertIn(new_member, project.project_members.all(), "El miembro no fue agregado al proyecto")
        self.assertIn(self.scrum_rol, member.roles.all(), "El rol no fue agregado al miembro")

    def test_member_has_roles(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data)
        roles = ['Scrum Master']
        result = ProjectUseCase.member_has_roles(user_id=self.scrum_master.id, project_id=project.id, roles=roles)
        self.assertTrue(result, "El miembro debe tener el rol Scrum Master")

    def test_member_has_permissions(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data)
        new_user = CustomUser.objects.create(
            first_name='New',
            last_name='Member',
            email='newmember@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user'
        )
        new_member = ProjectMember.objects.create(
            user=new_user,
            project=project,
        )
        new_member.roles.add(self.scrum_rol)
        permissions = ['ABM Roles']
        permissions_false = ['ABM Proyectos']
        result_true = ProjectUseCase.member_has_permissions(user_id=self.scrum_master.id, project_id=project.id, permissions=permissions)
        result_false = ProjectUseCase.member_has_permissions(user_id=self.scrum_master.id, project_id=project.id, permissions=permissions_false)
        self.assertTrue(result_true, "El miembro debe tener el permiso ABM Roles")
        self.assertFalse(result_false, "El miembro no debe tener el permiso ABM Proyectos")


