from django.db.models import Q
from users.models import CustomUser


class UserUseCase:

    @staticmethod
    def update_system_role(user_id, role):
        """
            Metodo para actualizar el rol de sistema de un usuario
        """
        user = CustomUser.objects.get(id=user_id)
        user.role_system = role
        user.save()
        return user

    @staticmethod
    def users_by_filter(search):
        """
            Metodo para buscar usuarios por nombre, apellido, correo o rol de sistema
        """
        return CustomUser.objects.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(role_system__icontains=search)
        )

