from django.db import models
from django.contrib.auth.models import User
from board_app.models import Board

class Task(models.Model):
    """
    Model representing a task in the Kanban board system.

    Attributes:
        board (ForeignKey): The board this task belongs to.
        title (CharField): The title of the task.
        description (CharField): A brief description of the task.
        status (CharField): The current status of the task (e.g., 'to-do', 'in_progress').
        priority (CharField): The priority level of the task (e.g., 'low', 'medium', 'high').
        assignee (ForeignKey): The user assigned to the task.
        reviewer (ForeignKey): The user reviewing the task.
        due_date (DateField): The due date for the task.
        comments_count (IntegerField): The number of comments on the task.
    """


    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ]
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255) 
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewed_tasks', null=True, blank=True)
    due_date = models.DateField()
    comments_count = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        """
        Return a string representation of the task.

        Returns:
           str: The title of the task.
        """
        return self.title
    
class TaskCommentsModel(models.Model):
    """
    Model representing comments on a task.

    Attributes:
        task (ForeignKey): The task this comment belongs to.
        author (ForeignKey): The user who wrote the comment.
        content (TextField): The content of the comment.
        created_at (DateTimeField): The timestamp when the comment was created.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_author')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        """
        Return a string representation of the comment.

        Returns:
          str: A truncated version of the comment showing the author and content.
        """
        return f"{self.author.username}: {self.content[:20]}"
