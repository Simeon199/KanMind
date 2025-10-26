from django.db import models
from django.contrib.auth.models import User
from board_app.models import Board

# class Assignee(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     board = models.ForeignKey(Board, related_name='assignees', on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.user.username} - {self.board.title}"

# class Reviewer(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     board = models.ForeignKey(Board, related_name='reviewers', on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.user.username} - {self.board.title}"

class Task(models.Model):
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255) 
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewed_tasks', null=True, blank=True)
    due_date = models.DateField()

    def __str__(self):
        return self.title
                