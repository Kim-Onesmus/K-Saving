from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Client(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    username = models.PositiveIntegerField(max_length=13)
    
    def __str__(self):
        return self.first_name
    