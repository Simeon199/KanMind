from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_of_board')
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return f"{self.title}"
    
class SingleBoard(models.Model):
    title = models.CharField(max_length=255)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_of_board', null=True, blank=True)
    members = models.ManyToManyField(User, related_name='board_members')

    def __str__(self):
        return f"{self.title}"
