from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"
    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (INSTRUCTOR, "Instructor"),
    ]
    role = models.CharField( max_length=20,choices=ROLE_CHOICES,default=STUDENT,)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    bio = models.TextField(blank=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"