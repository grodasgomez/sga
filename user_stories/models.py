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

class UserStoryTask(models.Model):
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    sprint = models.ForeignKey('sprints.Sprint', on_delete=models.CASCADE, null=True)
    sprint_member = models.ForeignKey('sprints.SprintMember', on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=100)
    hours_worked = models.IntegerField(default=0)
    column = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

def us_directory_path(instance, filename):
    return f"user_stories/{instance.user_story.code}/{filename}"
class UserStoryAttachment(models.Model):
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    file = models.FileField(upload_to=us_directory_path, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def filename(self):
        return self.file.name.split('/')[-1]

    @property
    def size(self):
        # Return a string with the size and the unit
        amountOfDivisions = 0
        size = self.file.size
        while size > 1024:
            size = size / 1024
            amountOfDivisions += 1
        units = {
            0: 'B',
            1: 'KB',
            2: 'MB',
            3: 'GB',
            4: 'TB',
        }
        return f"{round(size, 2)} {units[amountOfDivisions]}"
    def __str__(self):
        return self.user_story.code

    class Meta:
        ordering = ['id']

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
