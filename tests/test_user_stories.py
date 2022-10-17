from django.test import TestCase
from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()
from projects.models import Permission, Project, ProjectMember, Role, UserStoryType
from projects.usecase import ProjectUseCase, RoleUseCase
from user_stories.usecase import UserStoriesUseCase
from users.models import CustomUser


class UserStoriesUseCaseTest(TestCase):
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

    def test_create_user_story_history(self):
        project_id = self.project.id
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project_id)
        data = {
            'code':str(project_id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project_id)+1),
            'title': 'User Story 1',
            'description': 'Descripcion del user story 1',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project_id,
        }

        user1 = CustomUser()
        user1.role_system = "user"
        user1.email = "user1@gmail.com"
        user1.save()

        project_member = ProjectMember.objects.create(
            project=self.project,
            user=user1
        )

        user_story = ProjectUseCase.create_user_story(**data)
        data['business_value']=3
        data.pop('code')
        data.pop('project_id')
        new_user_story = ProjectUseCase.edit_user_story(user_story.id,**data)

        user_story_history=UserStoriesUseCase.create_user_story_history(user_story,new_user_story,user1,project_id)

        self.assertIn(user_story_history, UserStoriesUseCase.user_story_history_by_us_id(user_story.id), "La version del user story no fue agregado al proyecto")


    def test_restore_user_story(self):
            project_id = self.project.id
            us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project_id)
            data = {
                'code':str(project_id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project_id)+1),
                'title': 'User Story 1',
                'description': 'Descripcion del user story 1',
                'technical_priority': 1,
                'business_value': 2,
                'estimation_time': 1,
                'us_type': us_type,
                'project_id': project_id,
            }

            user1 = CustomUser()
            user1.role_system = "user"
            user1.email = "user1@gmail.com"
            user1.save()

            project_member = ProjectMember.objects.create(
                project=self.project,
                user=user1
            )

            user_story = ProjectUseCase.create_user_story(**data)
            data['business_value']=3
            data.pop('code')
            data.pop('project_id')
            new_user_story = ProjectUseCase.edit_user_story(user_story.id,**data)

            user_story_history=UserStoriesUseCase.create_user_story_history(user_story,new_user_story,user1,project_id)

            data=user_story_history.dataJson
            data["us_type"]=ProjectUseCase.get_user_story_type(data["us_type"])
            data["sprint"]=None
            data["sprint_member"]=None

            restored_user_story=UserStoriesUseCase.restore_user_story(user_story.id,**data)

            self.assertEqual(restored_user_story, user_story, "La version del user story no fue restaurada en el proyecto")
