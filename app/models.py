from django.db import models
from django.contrib.auth.models import User
from .utils import generate_default_profile_picture
from django.conf import settings
import os
# Create your models here.

myPlan = [
    ('daily','daily'),
    ('weekly','weekly'),
    ('monthly','monthly'),
]

def user_profile_picture_path(instance, filename):
    # Generate a unique filename for the profile picture
    ext = filename.split('.')[-1]
    filename = f'media/{instance.user.username}_profile_pic.{ext}'
    return os.path.join(settings.MEDIA_ROOT, filename)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='media', default='media/bg0.png')
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

class My_Plan(models.Model):
    plan = models.CharField(max_length=100, choices=myPlan)
    amount = models.PositiveIntegerField()
    target = models.PositiveIntegerField()
    
    def __str__(self):
        return self.plan

class ContactUs(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    messange = models.TextField(max_length=200)
    
    def __str__(self):
        return self.name
    
    
class Pay(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    number = models.PositiveBigIntegerField(max_length=13)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

   
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# M-pesa Payment models

class MpesaCalls(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'


class MpesaCallBacks(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'


class MpesaPayment(BaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.TextField()
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'

    def __str__(self):
        return self.first_name    
    
    
    
class Withdraw(models.Model):
    number = models.PositiveBigIntegerField(max_length=13)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.number