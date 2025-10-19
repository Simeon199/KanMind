from django.db import models
# from django.contrib.auth.models import User

class UserProfile(models.Model):
    token = models.CharField(max_length=140, default='DEFAULT')
    fullname = models.CharField(max_length=30)
    email = models.EmailField()
    user_id = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.fullname}"