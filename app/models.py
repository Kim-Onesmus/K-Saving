from django.db import models
from django.contrib.auth.models import User
from .utils import generate_default_profile_picture
# Create your models here.

def user_profile_picture_path(instance, filename):
    # Generate a unique filename for the profile picture
    ext = filename.split('.')[-1]
    filename = f'media/{instance.user.username}_profile_pic.{ext}'
    return os.path.join(settings.MEDIA_ROOT, filename)

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
        
    def update_profile_picture(self, image):
        # Update the profile picture
        self.profile_picture = image
        self.save()
        
        
    def __str__(self):
        return self.first_name
    
    

class ContactUs(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    messange = models.TextField(max_length=200)
    
    def __str__(self):
        return self.name