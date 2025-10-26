from django.db import models
from auth_app.models import UserProfile

# class Assignee(models.Model):
#     id = models.AutoField(primary_key=True)
#     email = models.EmailField()
#     fullname = models.CharField(max_length=255)

#     def __str__(self):
#         return self.id

# class Reviewer(models.Model):
#     id = models.AutoField(primary_key=True)
#     email = models.EmailField()
#     fullname = models.CharField(max_length=255)

#     def __str__(self):
#         return self.id

class Task(models.Model):
    board = models.IntegerField()
    title = models.CharField(max_length=255) 
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    assignee_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assigned_tasks')
    reviewer_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviewed_tasks')
    due_date = models.DateField()

    def __str__(self):
        return self.title
                