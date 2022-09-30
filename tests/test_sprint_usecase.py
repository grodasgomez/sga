from django.test import TestCase
from django import setup
import os
from projects.usecase import ProjectUseCase
from sprints.models import SprintStatus

from sprints.usecase import SprintUseCase
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()
from projects.models import Permission, Project, ProjectMember, Role, UserStoryType
from users.models import CustomUser
from user_stories.models import UserStory

class SprintUseCaseTest(TestCase):
    def setUp(self):
        """
        Funcion que crea los datos iniciales en la base datos para los tests
        estos perduran durante toda la ejecucion de los tests
        """
        self.project = Project.objects.create(
            name='Proyecto 1',
            description='Descripcion del proyecto 1',
            prefix='P1',
            status='IN_PROGRESS',
        )
        self.scrum_rol = Role.objects.create(
            name='Scrum Master',
            description='Scrum Master',
        )
        self.user_story_type = ProjectUseCase.create_default_user_story_type(project_id=self.project.id)


    def test_create_sprint(self):
        project_id = self.project.id
        expected_sprint = {
            'capacity': 0,
            'status': SprintStatus.CREATED.value,
            'number': 1,
        }
        sprint = SprintUseCase.create_sprint(project_id, duration=14)
        self.assertDictContainsSubset(expected_sprint, sprint.__dict__, 'El sprint creado no es el esperado')

    def test_get_last_sprint(self):
        project_id = self.project.id
        duration = 14
        SprintUseCase.create_sprint(project_id, duration=14)
        sprint2 = SprintUseCase.create_sprint(project_id, duration=14)
        last_sprint = SprintUseCase.get_last_sprint(project_id)
        self.assertEqual(last_sprint.id, sprint2.id, 'El ultimo sprint no es el esperado')

    def test_exists_created_sprint(self):
        project_id = self.project.id
        self.assertFalse(SprintUseCase.exists_created_sprint(project_id), 'No deberia existir un sprint creado')

        sprint = SprintUseCase.create_sprint(project_id, duration=14)
        self.assertTrue(SprintUseCase.exists_created_sprint(project_id), 'Deberia existir un sprint creado')

        sprint.status = SprintStatus.IN_PROGRESS.value
        sprint.save()
        self.assertFalse(SprintUseCase.exists_created_sprint(project_id), 'No deberia existir un sprint creado')



    def test_exists_active_sprint(self):
        project_id = self.project.id
        self.assertFalse(SprintUseCase.exists_active_sprint(project_id), 'No deberia existir un sprint activo')

        sprint = SprintUseCase.create_sprint(project_id, duration=14)
        self.assertFalse(SprintUseCase.exists_active_sprint(project_id), 'No deberia existir un sprint activo')

        sprint.status = SprintStatus.IN_PROGRESS.value
        sprint.save()
        self.assertTrue(SprintUseCase.exists_active_sprint(project_id), 'Deberia existir un sprint activo')

    def test_get_addable_users(self):
        scrum_master = CustomUser.objects.create(
            first_name='Scrum',
            last_name='Master',
            email='scrum_master@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        developer = CustomUser.objects.create(
            first_name='Developer',
            last_name='Python',
            email='developer@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        scrum_role = Role.objects.create(
            name='Scrum Master',
            description='Scrum Master',
        )
        developer_role = Role.objects.create(
            name='Developer',
            description='developer',
        )
        ProjectUseCase.add_member(user = scrum_master, project_id = self.project.id, roles = [scrum_role])
        ProjectUseCase.add_member(user = developer, project_id = self.project.id, roles = [developer_role])
        sprint = SprintUseCase.create_sprint(self.project.id, duration=14)
        addable_users = SprintUseCase.get_addable_users(self.project.id, sprint.id)

        self.assertEqual(len(addable_users), 1, 'No se obtuvieron los usuarios esperados')

    def test_add_sprint_member(self):
        sprint = SprintUseCase.create_sprint(self.project.id, duration=14)
        developer = CustomUser.objects.create(
            first_name='Developer',
            last_name='Python',
            email='developer@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        data = {
            'workload': 10,
        }
        SprintUseCase.add_sprint_member(user = developer, sprint_id=sprint.id, **data)

    def test_edit_sprint_member(self):
        sprint = SprintUseCase.create_sprint(self.project.id, duration=14)
        developer = CustomUser.objects.create(
            first_name='Developer',
            last_name='Python',
            email='developer@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        data = {
            'workload': 10,
        }
        member = SprintUseCase.add_sprint_member(user = developer, sprint_id=sprint.id, **data)

        member = SprintUseCase.edit_sprint_member(member.id, 20)

        self.assertEqual(member.workload, 20, 'No se edito el miembro del sprint')

    def test_get_sprint_members(self):
        sprint = SprintUseCase.create_sprint(self.project.id, duration=14)
        members = SprintUseCase.get_sprint_members(sprint.id)
        self.assertEqual(len(members), 0, 'No deberia existir miembros en el sprint')

        developer = CustomUser.objects.create(
            first_name='Developer',
            last_name='Python',
            email='developer@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        data = {
            'workload': 10,
        }
        SprintUseCase.add_sprint_member(user = developer, sprint_id=sprint.id, **data)

        members = SprintUseCase.get_sprint_members(sprint.id)
        self.assertEqual(len(members), 1, 'Deberia existir un miembro en el sprint')

    def test_get_assignable_us_to_sprint(self):
        sprint = SprintUseCase.create_sprint(self.project.id, duration=14)
        us_list = SprintUseCase.assignable_us_to_sprint(self.project.id, sprint.id)
        self.assertEqual(us_list.count(), 0, 'No deberia existir user stories asignables al sprint')
        us = ProjectUseCase.create_user_story(
            code="US-1",
            title='User Story 1',
            description='User Story 1',
            business_value=1,
            technical_priority=1,
            estimation_time=1,
            us_type=self.user_story_type,
            project_id=self.project.id,
        )
        us_list = SprintUseCase.assignable_us_to_sprint(self.project.id, sprint.id)
        self.assertEqual(us_list.count(), 1, 'Deberia existir un user story asignable al sprint')
