from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from user_stories.models import UserStory

class UserStoryStatusMixin(AccessMixin):
	"""
	Clase que verifica si el estado del user story es el correcto
	"""
	def dispatch(self, request, *args, **kwargs):
		# Se obtiene el project_id de la url
		project_id = self.kwargs['project_id']
		user_story_id = self.kwargs.get('us_id')
		if not user_story_id:
			user_story_id = self.kwargs.get('user_story_id')
		us = UserStory.objects.get(id=user_story_id)
		if us.status == "CANCELLED" or us.status == "FINISHED":
			return self.handle_no_status()
		return super().dispatch(request, *args, **kwargs)

	def handle_no_status(self):
		messages.warning(self.request, 'La US no puede ser modificada')
		# en el caso en que el error te redirija a la misma pagina, bucle infinito
		if self.request.build_absolute_uri() == self.request.META.get('HTTP_REFERER'):
			return redirect(reverse('index'))
		return redirect(self.request.META.get('HTTP_REFERER', '/'))
