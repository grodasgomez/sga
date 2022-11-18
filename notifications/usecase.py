from .models import Notification
from django.urls import reverse
from projects.usecase import ProjectUseCase


class NotificationUseCase:

    @staticmethod
    def get_unread_notifications(user):
        """
        Obtiene las notificaciones no leidas del usuario
        """
        notifications = Notification.objects.filter(user=user, read=False)
        return notifications

    @staticmethod
    def get_notifications(user):
        """
        Obtiene las notificaciones del usuario
        """
        notifications = Notification.objects.filter(
            user=user).order_by('-created_at')
        return notifications

    @staticmethod
    def mark_notification_as_read(notification_id):
        """
        Marca una notificacion como leida
        """
        notification = Notification.objects.get(id=notification_id)
        notification.read = True
        notification.save()
        return notification

    @staticmethod
    def notify_add_member_to_project(user, project):
        """
        Notifica a un usuario que ha sido agregado a un proyecto
        """
        url = reverse('projects:project-detail',
                      kwargs={'project_id': project.id})
        project_str = f"<a href='{url}'>{project.name}</a>"
        content = f'Ahora eres nuevo miembro del proyecto {project_str}'
        title = f"Agregado al proyecto {project.name}"
        Notification.objects.create(user=user, content=content, title=title)

    @staticmethod
    def notify_assign_us(user, user_story):
        """
        Notifica a un usuario que se le ha asignado un user story
        """
        project = user_story.project
        url = reverse('projects:project-backlog-detail',
                      kwargs={'project_id': project.id, 'us_id': user_story.id})
        us_str = f"<a href='{url}'>{user_story.code}</a>"
        content = f'Se te ha asignado la US {us_str}'
        title = f"US asignado {user_story.code}"
        Notification.objects.create(user=user, content=content, title=title)

    @staticmethod
    def notify_add_member_to_sprint(sprint_member):
        """
        Notifica a un usuario que ha sido agregado a un sprint
        """
        sprint = sprint_member.sprint
        project = sprint.project
        user = sprint_member.user
        url = reverse('projects:sprints:detail', kwargs={
                      'project_id': project.id, 'sprint_id': sprint.id})
        sprint_str = f"<a href='{url}'>{sprint.name}</a>"
        content = f'Se te ha agregado al {sprint_str} con una carga de trabajo igual a {sprint_member.workload} horas'
        title = f"Agregado al sprint {sprint.name}"
        Notification.objects.create(user=user, content=content, title=title)

    @staticmethod
    def notify_comment_us(user_story):
        """
        Notifica a un usuario que se ha creado un comentario a su us asignada
        """
        project = user_story.sprint.project
        user = user_story.sprint_member.user
        url = reverse('projects:project-backlog-detail',
                      kwargs={'project_id': project.id, 'us_id': user_story.id})
        us_str = f"<a href='{url}'>{user_story.code}</a>"
        content = f'Se ha creado un comentario en la US {us_str}'
        title = f"Comentario en US {user_story.code}"
        Notification.objects.create(user=user, content=content, title=title)

    @staticmethod
    def notify_change_us_column(user_story, scrum_master_email):
        """
        Notifica a un usuario que se ha cambiado la columna de su us asignada
        """
        project = user_story.sprint.project
        user = user_story.sprint_member.user
        url = reverse('projects:project-backlog-detail',
                      kwargs={'project_id': project.id, 'us_id': user_story.id})
        us_str = f"<a href='{url}'>{user_story.code}</a>"
        new_column = user_story.column_name
        content = f'Se ha cambiado la columna de la US {us_str} a {new_column} por el scrum master {scrum_master_email}'
        title = f"Cambio de columna en US {user_story.code}"
        Notification.objects.create(user=user, content=content, title=title)

    @staticmethod
    def notify_done_us(user_story):
        """
        Notifica a los scrum masters de un proyecto que una us está en la columna DONE
        """
        project = user_story.sprint.project
        project_members = ProjectUseCase.get_project_scrum_masters(project.id)

        # Para no notificar al usuario asignado que puede ser scrum master del proyecto
        if(user_story.sprint_member):
            project_members = project_members.exclude(
                user__id=user_story.sprint_member.user.id)

        url = reverse('projects:project-backlog-detail',
                      kwargs={'project_id': project.id, 'us_id': user_story.id})
        us_str = f"<a href='{url}'>{user_story.code}</a>"

        content = f'La US {us_str} ha sido movida a la columna DONE'
        title = f"US {user_story.code} en DONE"

        for project_member in project_members:
            Notification.objects.create(
                user=project_member.user, content=content, title=title)
