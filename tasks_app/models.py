from django.db import models

from board_app.models import Board

class Task(models.Model):
    board = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    assignee_id = models.IntegerField()
    reviewer_id = models.IntegerField()
    due_date = models.IntegerField()

# class Task(models.Model):
#     Board = 'board'
#     title = 'title'
#     description = 'description'
#     status = 'status'
#     priority = 'priority'
#     assignee_id = 'assignee_id'
#     reviewer_id = 'reviewer_id'
#     due_date = 'due_date'

    # class Assignee(models.Model):
    #     id = models.AutoField(primary_key=True)
    #     email = models.EmailField()
    #     fullname = models.CharField(max_length=255)

    #     def __str__(self):
    #         return self.email
        
    # class Reviewer(models.Model):
    #     id = models.AutoField(primary_key=True)
    #     email = models.EmailField()
    #     fullname = models.CharField(max_length=255)

    #     def __str__(self):
    #         return self.email

    # class TaskAssignee(models.Model):
    #     task = models.ForeignKey(task, on_delete=models.CASCADE)
    #     assignee = models.ForeignKey(assignee, on_delete=models.CASCADE)

    #     def __str__(self):
    #         return f"{self.assignee.fullname} - {self.task.title}"

    # class TaskReview(models.Model):
    #     task = models.ForeignKey(task, on_delete=models.Model)
    #     reviewer = models.ForeignKey(reviewer, on_delete=models.CASCADE)
    #     comments_count = models.PositiveIntegerField(default=0)

    #     def __str__(self):
    #         return f"{self.reviewer.fullname} - {self.task.description} - {self.comments_count}"
                