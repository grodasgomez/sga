from django.db.models import Q
from users.models import CustomUser


class UserUseCase:

    @staticmethod
    def update_system_role(user_id, role):
        user = CustomUser.objects.get(id=user_id)
        user.role_system = role
        user.save()
        return user

