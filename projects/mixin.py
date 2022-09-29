from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from projects.usecase import ProjectUseCase

class ProjectPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Clase que verifica que el usuario este logueado, que tenga una lista de permisos
    o una lista de roles para realizar la accion en el proyecto
    """
    permissions = None
    roles = None

    def has_permission(self):
        # Se obtiene el usuario logueado
        user = self.request.user
        # Se obtiene el id del proyecto de la url
        project_id = self.kwargs['project_id']
        # Se verifica que el usuario tenga el permiso
        has_perm = ProjectUseCase.member_has_permissions(user.id, project_id, self.permissions)
        # Se verifica que el usuario tenga el rol
        has_role = ProjectUseCase.member_has_roles(user.id, project_id, self.roles)

        return has_perm or has_role

    def handle_no_permission(self) -> HttpResponseRedirect:
        """
        Metodo que se ejecuta cuando el usuario no tiene permisos para acceder a la vista
        """
        messages.warning(self.request, 'No tienes permisos para realizar esta accion')
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))
