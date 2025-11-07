from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_boards', blank=True, null=True) # Neu: blank=True, null=True
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return f"{self.title}"

class SingleBoard(models.Model):
    title = models.CharField(max_length=255)