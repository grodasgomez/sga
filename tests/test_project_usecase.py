from django.test import TestCase
from django import setup
from django.core.files.uploadedfile import SimpleUploadedFile
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()
from projects.models import Permission, Project, ProjectMember, Role, UserStoryType
from projects.usecase import ProjectUseCase, RoleUseCase
from sprints.usecase import SprintUseCase
from users.models import CustomUser

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

    def test_cancel_project(self):
        data = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data)
        ProjectUseCase.cancel_project(project.id)
        project = Project.objects.get(id=project.id)
        self.assertTrue(project.status=='CANCELLED', "El proyecto no fue cancelado")

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

    def test_create_role(self):
        data = {
            'name': 'Rol nuevo prueba',
            'description': 'Prueba de creacion de rol',
        }
        data_project = {
            'name': 'Proyecto 2',
            'description': 'Descripcion del proyecto 2',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }

        project = ProjectUseCase.create_project(**data_project) #creacion de proyecto
        permissions = [self.permission] #tomamos un permiso
        role=RoleUseCase.create_role(project.id,data['name'],data['description'],permissions) #creamos el rol

        self.assertIn(role, RoleUseCase.get_roles_by_project_no_default(project.id), "El rol no fue agregado al proyecto")
        self.assertIn(self.permission, role.permissions.all(), "El permiso no fue agregado al rol")

    def test_edit_role(self):
        data_original = {
            'name': 'Rol nuevo prueba',
            'description': 'Prueba de creacion de rol',
        }
        data = {
            'name': 'Rol edit prueba',
            'description': 'Prueba de edicion de rol',
        }
        data_project = {
            'name': 'Proyecto 3',
            'description': 'Descripcion del proyecto 3',
            'prefix': 'P3',
            'scrum_master': self.scrum_master,
        }

        project = ProjectUseCase.create_project(**data_project) #creacion de proyecto
        permissions = [self.permission] #tomamos un permiso
        role=RoleUseCase.create_role(project.id,data_original['name'],data_original['description'],permissions) #creamos el rol

        new_permission=Permission.objects.create(name="Nuevo permiso",description="Nuevo permiso de prueba")
        permissions_new = [new_permission] #tomamos un permiso nuevo
        #permissions_new = [self.permission,new_permission] #tomamos dos permisos para hacer fallar

        RoleUseCase.edit_role(role.id,data['name'],data['description'],permissions_new) #editamos el rol
        role=RoleUseCase.get_role_by_id(role.id)

        self.assertIn(role, RoleUseCase.get_roles_by_project_no_default(project.id), "El rol no fue agregado al proyecto")
        self.assertNotIn(self.permission, role.permissions.all(), "El permiso no fue borrado al rol")
        self.assertIn(new_permission, role.permissions.all(), "El permiso no fue agregado al rol")

    def test_create_user_story(self):
        data1 = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data1)
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)
        data = {
            'code':str(project.id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project.id)+1),
            'title': 'User Story 1',
            'description': 'Descripcion del user story 1',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project.id,
        }

        user_story = ProjectUseCase.create_user_story(**data)
        self.assertIn(user_story, ProjectUseCase.user_stories_by_project(project.id), "El user story no fue agregado al proyecto")

    def test_count_user_stories_by_project(self):
        data1 = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data1)
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)
        data = {
            'code':str(project.id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project.id)+1),
            'title': 'User Story 1',
            'description': 'Descripcion del user story 1',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project.id,
        }

        user_story = ProjectUseCase.create_user_story(**data)
        self.assertNotEqual(ProjectUseCase.count_user_stories_by_project(project.id), 0, "NO hay historias de usuario")

    def test_user_stories_by_project_filter(self):
        data1 = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data1)
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)
        data = {
            'code':str(project.id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project.id)+1),
            'title': 'User Story 1',
            'description': 'Descripcion del user story 1',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project.id,
        }
        user_story1 = ProjectUseCase.create_user_story(**data)
        data = {
            'code':str(project.id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project.id)+1),
            'title': 'User Story 2',
            'description': 'Descripcion del user story 2',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project.id,
        }
        user_story2 = ProjectUseCase.create_user_story(**data)

        busqueda = "User Story 1"
        found_us = ProjectUseCase.user_stories_by_project_filter(project.id,us_type.id,busqueda)
        self.assertEqual(len(found_us), 1, "No se encontro la cantidad debida de historias de usuario")

        busqueda = "Descripcion del user story 1"
        found_us = ProjectUseCase.user_stories_by_project_filter(project.id,us_type.id,busqueda)
        self.assertEqual(len(found_us), 1, "No se encontro la cantidad debida de historias de usuario")

        busqueda = "Descripcion del user story"
        found_us = ProjectUseCase.user_stories_by_project_filter(project.id,us_type.id,busqueda)
        self.assertEqual(len(found_us), 2, "No se encontro la cantidad debida de historias de usuario")

        #filtro encontrara las dos ya que tienen mismo tipo
        filtro = us_type.id
        busqueda = ""
        found_us = ProjectUseCase.user_stories_by_project_filter(project.id,filtro,busqueda)
        self.assertEqual(len(found_us), 2, "No se encontro la cantidad debida de historias de usuario")

    def test_create_attachment(self):
        data1 = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data1)
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)
        data = {
            'code':str(project.id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project.id)+1),
            'title': 'User Story 1',
            'description': 'Descripcion del user story 1',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project.id,
        }
        user_story1 = ProjectUseCase.create_user_story(**data)
        file = SimpleUploadedFile("file.txt", b"file_content")
        attachment = ProjectUseCase.create_attachment(user_story1.id, file)
        self.assertEqual(attachment.user_story.id, user_story1.id, "El archivo no fue agregado a la historia de usuario")
        ProjectUseCase.delete_attachment(attachment.id)

    def test_get_attachments_by_user_story(self):
        data1 = {
            'name': 'Proyecto 1',
            'description': 'Descripcion del proyecto 1',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }
        project = ProjectUseCase.create_project(**data1)
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)
        data = {
            'code':str(project.id)+"-"+str(ProjectUseCase.count_user_stories_by_project(project.id)+1),
            'title': 'User Story 1',
            'description': 'Descripcion del user story 1',
            'technical_priority': 1,
            'business_value': 2,
            'estimation_time': 1,
            'us_type': us_type,
            'project_id': project.id,
        }
        user_story1 = ProjectUseCase.create_user_story(**data)
        file = SimpleUploadedFile("file.txt", b"file_content")
        file2 = SimpleUploadedFile("file2.txt", b"file_content2")
        attachment = ProjectUseCase.create_attachment(user_story1.id, file)
        attachment2 = ProjectUseCase.create_attachment(user_story1.id, file2)
        attachments = ProjectUseCase.get_attachments_by_user_story(user_story1.id)
        self.assertEqual(len(attachments), 2, "No se encontraron los archivos")
        ProjectUseCase.delete_attachment(attachment.id)
        ProjectUseCase.delete_attachment(attachment2.id)

    def test_create_holiday(self):
        """
        Funcion que prueba la creacion de un feriado
        """
        data = {
            'date': '2022-11-4',
        }
        data_project = {
            'name': 'Proyecto 2',
            'description': 'Descripcion del proyecto 2',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }

        project = ProjectUseCase.create_project(**data_project) #creacion de proyecto
        holiday=ProjectUseCase.create_holiday(project_id=project.id,date=data['date']) #creacion de feriado

        self.assertIn(holiday, ProjectUseCase.get_holidays_by_project(project.id), "El feriado no fue agregado al proyecto")

    
    def test_delete_holiday(self):
        """
        Funcion que prueba la eliminacion de un feriado
        """
        data = {
            'date': '2022-11-4',
        }
        data_project = {
            'name': 'Proyecto 2',
            'description': 'Descripcion del proyecto 2',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }

        project = ProjectUseCase.create_project(**data_project) #creacion de proyecto
        holiday = ProjectUseCase.create_holiday(project_id=project.id,date=data['date']) #creacion de feriado
        holiday = ProjectUseCase.delete_holiday(holiday.id) #eliminacion de feriado

        self.assertNotIn(holiday, ProjectUseCase.get_holidays_by_project(project.id), "El feriado no fue eliminado del proyecto")
    

    def test_update_end_date_of_sprint_when_create_a_holiday(self):
        """
        Funcion que prueba la actualizacion de la fecha estimada de un sprint cuando se crea un feriado
        """
        data = {
            'date': '2022-11-07',
        }
        data_project = {
            'name': 'Proyecto 2',
            'description': 'Descripcion del proyecto 2',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }

        project = ProjectUseCase.create_project(**data_project) #creacion de proyecto
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)

        sprint = SprintUseCase.create_sprint(project.id, duration=5)
        developer = CustomUser.objects.create(
            first_name='Developer',
            last_name='Python',
            email='developer@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        SprintUseCase.add_sprint_member(user = developer, sprint_id=sprint.id, **{'workload': 10})

        us = ProjectUseCase.create_user_story(code="US-1", title='User Story 1', description='User Story 1',
                                                business_value=1, technical_priority=1, estimation_time=1,
                                                us_type=us_type, project_id=project.id)

        SprintUseCase.assign_us_sprint(sprint.id, us.id)
        SprintUseCase.start_sprint(sprint)
        sprint = SprintUseCase.get_sprint_by_id(sprint.id)
        old_end_date=sprint.end_date

        holiday = ProjectUseCase.create_holiday(project_id=project.id,date=data['date']) #creacion de feriado
        sprint=SprintUseCase.recalculate_sprint_end_date(SprintUseCase.get_current_sprint(project.id))

        self.assertNotEqual(old_end_date, sprint.end_date, "La fecha de fin del sprint sigue siendo la misma despues de agregar un feriado en un dia habil")
    
    def test_update_end_date_of_sprint_when_delete_a_holiday(self):
        """
        Funcion que prueba la actualizacion de la fecha estimada de un sprint cuando se borra un feriado
        """
        data = {
            'date': '2022-11-07',
        }
        data_project = {
            'name': 'Proyecto 2',
            'description': 'Descripcion del proyecto 2',
            'prefix': 'P1',
            'scrum_master': self.scrum_master,
        }

        project = ProjectUseCase.create_project(**data_project) #creacion de proyecto
        us_type=ProjectUseCase.create_user_story_type("Tipo de user story de prueba",['Por hacer', 'En progreso', 'Hecho'],project.id)

        sprint = SprintUseCase.create_sprint(project.id, duration=5)
        developer = CustomUser.objects.create(
            first_name='Developer',
            last_name='Python',
            email='developer@gmail.com',
            password='dsad',
            is_active=True,
            role_system='user')
        SprintUseCase.add_sprint_member(user = developer, sprint_id=sprint.id, **{'workload': 10})

        us = ProjectUseCase.create_user_story(code="US-1", title='User Story 1', description='User Story 1',
                                                business_value=1, technical_priority=1, estimation_time=1,
                                                us_type=us_type, project_id=project.id)

        SprintUseCase.assign_us_sprint(sprint.id, us.id)
        holiday = ProjectUseCase.create_holiday(project_id=project.id,date=data['date']) #creacion de feriado
        SprintUseCase.start_sprint(sprint)
        sprint = SprintUseCase.get_sprint_by_id(sprint.id)
        old_end_date=sprint.end_date

        holiday = ProjectUseCase.delete_holiday(holiday.id) #eliminacion de feriado
        sprint=SprintUseCase.recalculate_sprint_end_date(SprintUseCase.get_current_sprint(project.id))

        self.assertNotEqual(old_end_date, sprint.end_date, "La fecha de fin del sprint sigue siendo la misma despues de borrar un feriado que era un dia habil")

        
