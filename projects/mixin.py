from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from projects.usecase import ProjectUseCase
from projects.models import Project, ProjectMember

class ProjectAccessMixin(AccessMixin):
    """
    Clase que verifica si el usuario es miembro del proyecto
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        project_id = self.kwargs['project_id']
        member = ProjectMember.objects.filter(project=project_id, user=user).exists()
        if not member:
            self.raise_exception = True
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.raise_exception:
            messages.warning(self.request, "No eres miembro del proyecto")
            # en el caso en que el error te redirija a la misma pagina, bucle infinito
            if self.request.build_absolute_uri() == self.request.META.get('HTTP_REFERER'):
                return redirect(reverse('index'))
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
        return super().handle_no_permission()

class ProjectPermissionMixin(AccessMixin):
    """
    Clase que verifica que si el usuario tiene permisos dada
    una lista de permisos o una lista de roles para realizar
    la accion en el proyecto
    """
    permissions = None
    roles = None

    def dispatch(self, request, *args, **kwargs):
        # Se obtiene el usuario logueado
        user = self.request.user
        # Se obtiene el id del proyecto de la url
        project_id = self.kwargs['project_id']
        if not self.has_permission(user, project_id):
            self.raise_exception = True
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, user, project_id):
        # Se verifica que el usuario tenga el permiso
        has_perm = ProjectUseCase.member_has_permissions(user.id, project_id, self.permissions)
        # Se verifica que el usuario tenga el rol
        has_role = ProjectUseCase.member_has_roles(user.id, project_id, self.roles)
        return has_perm or has_role

    def handle_no_permission(self):
        """
        Metodo que se ejecuta cuando el usuario no tiene permisos para acceder a la vista
        """
        if self.raise_exception:
            messages.warning(self.request, 'No tienes permisos para realizar esta accion')
            # en el caso en que el error te redirija a la misma pagina, bucle infinito
            if self.request.build_absolute_uri() == self.request.META.get('HTTP_REFERER'):
                return redirect(reverse('index'))
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
        return super().handle_no_permission()

class ProjectStatusMixin(AccessMixin):
    """
    Clase que verifica si el proyecto esta en estado de progreso,
    si no lo esta, no se pueden realizar modificaciones
    """
    def dispatch(self, request, *args, **kwargs):
        # Se obtiene el project_id de la url
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)
        if project.status == 'CANCELLED' or project.status == 'FINISHED':
            return self.handle_no_status()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_status(self):
        messages.warning(self.request, 'El proyecto no se puede modificar')
        # en el caso en que el error te redirija a la misma pagina, bucle infinito
        if self.request.build_absolute_uri() == self.request.META.get('HTTP_REFERER'):
            return redirect(reverse('index'))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
