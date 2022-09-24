from django.db import models

from projects.models import Project,UserStoryType
from sprints.models import Sprint, SprintMember

class UserStory(models.Model):
    code = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    business_value= models.IntegerField()
    technical_priority= models.IntegerField()
    estimation_time= models.IntegerField()
    us_type= models.ForeignKey(UserStoryType, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, null=True)
    sprint_member = models.ForeignKey(SprintMember, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['code']
