from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return f"{self.title}"
    