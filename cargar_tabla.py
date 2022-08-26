from users import models

# rol1 = models.Role()
# rol1.name = "Scrum Master"
# rol1.save()

# rol2 = models.Role()
# rol2.name = "Developer"
# rol2.save()

project1 = models.project()
project1.user_id = 2
project1.role_id = 34
project1.save()