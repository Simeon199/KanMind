from django.db import models

class UserProfile(models.Model):
    """
    Model representing a user profile in the authentication app.
    Stores additional user information such as token, fullname, email, and user ID.
    This model is linked to the Django User model via user_id. 
    """
    token = models.CharField(max_length=140, default='DEFAULT')
    fullname = models.CharField(max_length=30)
    email = models.EmailField()
    user_id = models.IntegerField(default=0)

    def __str__(self):
        """
        Return a string representation of the user profile.

        Returns:
           str: The fullname of the user profile.
        """
        return f"{self.fullname}"