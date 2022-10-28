from django.db import models
from django.forms.models import model_to_dict

from projects.models import Project,UserStoryType, ProjectMember
from users.models import CustomUser

class UserStory(models.Model):
    code = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    business_value= models.IntegerField()
    technical_priority= models.IntegerField()
    estimation_time= models.IntegerField()
    sprint_priority = models.IntegerField()
    us_type= models.ForeignKey(UserStoryType, on_delete=models.CASCADE)
    column = models.IntegerField(default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sprint = models.ForeignKey('sprints.Sprint', on_delete=models.CASCADE, null=True)
    sprint_member = models.ForeignKey('sprints.SprintMember', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.code

    def to_kanban_item(self):
        data = model_to_dict(self)
        if(self.sprint_member):
            user: CustomUser = self.sprint_member.user
            data['user'] = {
                'id': user.id,
                'name': user.name,
                'picture': user.picture
            }
        return data
    class Meta:
        ordering = ['id']

class UserStoryHistory(models.Model):
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    project_member = models.ForeignKey(ProjectMember, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    dataJson= models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.user_story.code

    class Meta:
        ordering = ['-created_at']

class UserStoryComment(models.Model):
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    project_member = models.ForeignKey(ProjectMember, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.user_story.code

    class Meta:
        ordering = ['-created_at']
