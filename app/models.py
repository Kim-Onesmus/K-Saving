from django.db import models
from django.contrib.auth.models import User
from .utils import generate_default_profile_picture
# Create your models here.

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='media')
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    username = models.PositiveIntegerField(max_length=13)
    
    def save(self, *args, **kwargs):
        if not self.profile_picture:
            self.profile_picture.name = generate_default_profile_picture(self.user)
        super().save(*args, **kwargs)
    
    

class ContactUs(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    messange = models.TextField(max_length=200)
    
    def __str__(self):
        return self.name