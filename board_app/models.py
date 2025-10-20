from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.CharField(max_length=255)
    member_count = models.PositiveIntegerField()
    ticket_count = models.PositiveIntegerField()
    tasks_to_do_count = models.PositiveBigIntegerField()
    tasks_high_prio_count = models.PositiveBigIntegerField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_board')

    def __str__(self):
        return self.title

# class Board(models.Model):
#     title = models.CharField(max_length=255)
#     member_count = models.PositiveIntegerField(default=0, blank=True)
#     ticket_count = models.PositiveIntegerField(default=0, blank=True)
#     tasks_to_do_count = models.PositiveIntegerField(default=0, blank=True)
#     tasks_high_prio_count = models.PositiveIntegerField(default=0, blank=True)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_board')
#     members = models.ManyToManyField(User, related_name='boards')

#     def __str__(self):
#         return self.title