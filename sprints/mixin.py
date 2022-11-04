from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseNotFound
from sprints.models import Sprint, SprintMember
from projects.usecase import ProjectUseCase

class SprintAccessMixin(AccessMixin):
    """
    Clase que verifica si el usuario es miembro del sprint
    o si es el scrum master del proyecto
    """
    is_scrum_master = False

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sprint_id = self.kwargs['sprint_id']
        project_id = self.kwargs['project_id']
        # Se verifica que la url tiene el proyecto correcto
        try:
            sprint = Sprint.objects.get(id=sprint_id, project=project_id)
        except:
            messages.warning(self.request, "Ha ocurrido un error en la url ඞ SUS")
            return redirect(reverse('index'))
        member = SprintMember.objects.filter(sprint=sprint_id, user=user).exists()
        self.is_scrum_master = ProjectUseCase.member_has_roles(user.id, project_id, ['Scrum Master'])
        if member or self.is_scrum_master:
            return super().dispatch(request, *args, **kwargs)
        self.raise_exception = True
        return self.handle_no_permission()

    def handle_no_permission(self):
        if self.raise_exception:
            messages.warning(self.request, "No eres miembro del sprint")
            # en el caso en que el error te redirija a la misma pagina, bucle infinito
            if self.request.build_absolute_uri() == self.request.META.get('HTTP_REFERER'):
                return redirect(reverse('index'))
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
        return super().handle_no_permission()

class SprintStatusMixin(AccessMixin):
    """
    Clase que verifica si el sprint esta en estado de progreso,
    si no lo esta, no se pueden realizar modificaciones
    """
    def dispatch(self, request, *args, **kwargs):
        # Se obtiene el sprint_id de la url
        sprint_id = self.kwargs['sprint_id']
        sprint = Sprint.objects.get(id=sprint_id)
        if sprint.status == 'CANCELLED' or sprint.status == 'FINISHED':
            return self.handle_no_status()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_status(self):
        messages.warning(self.request, 'El sprint no se puede modificar')
        # en el caso en que el error te redirija a la misma pagina, bucle infinito
        if self.request.build_absolute_uri() == self.request.META.get('HTTP_REFERER'):
            return redirect(reverse('index'))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
