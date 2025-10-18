from django.db import models
# from django.contrib.auth.models import User

class UserProfile(models.Model):
    token = models.CharField()
    fullname = models.CharField(max_length=30)
    email = models.EmailField()
    user_id = models.IntegerField()

    def __str__(self):
        return f"{self.fullname}"