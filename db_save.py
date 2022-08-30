from users import models

permis1 = models.permission()
permis1.name = "ABM Roles" 
permis1.description = "ABM de Roles"
permis1.save()

rol1 = models.role()
rol1.name = "Scrum Master"
rol1.save()

rol2 = models.role()
rol2.name = "Developer"
rol2.save()

rol1.permissions.add(permis1)

# project1 = models.project()
# project1.user_id = 2
# project1.role_id = 2
# project1.save()