from django.shortcuts import redirect, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class CustomLoginMixin(LoginRequiredMixin):
	"""
	Clase que permite verificar si el usuario esta logueado e implementa never_cache
	"""
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

class AdminMixin(AccessMixin):
	"""
	Clase que permite verificar si el usuario es administrador
	"""
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		if not request.user.is_admin():
			self.raise_exception = True
			return self.handle_no_permission()
		return super().dispatch(request, *args, **kwargs)

	def handle_no_permission(self):
		if self.raise_exception:
			messages.warning(self.request, "No tienes acceso a esta pagina")
			return redirect(self.request.META.get('HTTP_REFERER', '/'))
		return super().handle_no_permission()

class VerifiedMixin(AccessMixin):
	"""
	Clase que permite verificar si el usuario esta verificado
	"""
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		if not request.user.is_verified():
			self.raise_exception = True
			return self.handle_no_permission()
		return super().dispatch(request, *args, **kwargs)

	def handle_no_permission(self):
		if self.raise_exception:
			messages.warning(self.request, "No tienes acceso a esta pagina")
			return redirect(self.request.META.get('HTTP_REFERER', '/'))
		return super().handle_no_permission()

class UserMixin(AccessMixin):
	"""
	Clase que permite verificar si el usuario es un usuario
	"""
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return self.handle_no_permission()
		if not request.user.is_user():
			self.raise_exception = True
			return self.handle_no_permission()
		return super().dispatch(request, *args, **kwargs)

	def handle_no_permission(self):
		if self.raise_exception:
			messages.warning(self.request, "No tienes acceso a esta pagina")
			return redirect(self.request.META.get('HTTP_REFERER', '/'))
		return super().handle_no_permission()
