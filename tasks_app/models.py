from django.db import models
from auth_app.models import UserProfile

class Task(models.Model):
    board = models.IntegerField()
    title = models.CharField(max_length=255) # normal charfield
    description = models.CharField(max_length=255) # normal charfield
    status = models.CharField(max_length=255) # normal charfield
    priority = models.CharField(max_length=255) # normal charfield
    assignee_id = models.IntegerField()
    reviewer_id = models.IntegerField()
    due_date = models.IntegerField()

class Assignee(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    fullname = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class Reviewer(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    fullname = models.CharField(max_length=255)

    def __str__(self):
        return self.email
                