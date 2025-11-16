from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    """
    Model representing a board in the application.
    A board has a title, an owner (who created it), and multiple members.
    Members can collaborate on tasks associated with the board.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_boards', blank=True, null=True) # Neu: blank=True, null=True
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        """
        Return a string representation of the board.

        Returns:
           str: The title of the board.
        """
        return f"{self.title}"

class SingleBoard(models.Model):
    """
    Model representing a single board in the application.
    Includes owner, members, and associated tasks for detailed retrieval.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='single_owner_boards', blank=True, null=True)
    members = models.ManyToManyField(User, related_name='single_boards')