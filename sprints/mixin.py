from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from sprints.models import Sprint

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
