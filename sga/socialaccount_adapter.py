from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from users.models import CustomUser


class CustomUsersAccountAdapter(DefaultSocialAccountAdapter):
    """
    Clase encargada de la lógica de manejo de usuarios mediante cuentas sociales.
    """
    def new_user(self, request, sociallogin):
        """
        Instancia un nuevo usuario con los datos de la cuenta social.
        Si es el primer usuario que se registra, se le asigna el rol de administrador.
        """
        user = super().new_user(request, sociallogin)
        if CustomUser.objects.all().count() == 0:
            user.role_system = 'admin'
        return user
