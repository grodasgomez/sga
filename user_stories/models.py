from django.db import models

from projects.models import Project,UserStoryType

class UserStory(models.Model):
    code = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    business_value= models.IntegerField()
    technical_priority= models.IntegerField()
    estimation_time= models.IntegerField()
    us_type= models.ForeignKey(UserStoryType, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #sprint_member = models.ForeignKey(SprintMember, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

