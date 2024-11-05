from django.db import models
from django.contrib.auth.models import User
from .utils import generate_default_profile_picture
from django.core.validators import MinValueValidator
from django.conf import settings
import os
# Create your models here.

myPlan = [
    ('daily','daily'),
    ('weekly','weekly'),
    ('monthly','monthly'),
]

withdraw_status = [
    ('approved','approved'),
    ('pending','pending'),
    ('cancelled','cancelled'),
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
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
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
    pay_id = models.BigAutoField(primary_key=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    number = models.PositiveBigIntegerField(max_length=13)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Withdraw(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    withdraw_id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=200, choices=withdraw_status, default='pending')
    number = models.PositiveBigIntegerField(max_length=13)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    

class Notification(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message

   
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True





class MpesaCallBacks(models.Model):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.JSONField()  # Use JSONField to store JSON data
    callback_metadata = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)  # Status field to mark success or failure

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'

    def __str__(self):
        return f"{self.caller} - {self.status}"


class MpesaTransaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_time = models.CharField(max_length=14)  # or DateTimeField if you convert the string
    account_reference = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    payer_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments' 
    
    



class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class MpesaResponseBody(AbstractBaseModel):
    body = models.JSONField()


class Transaction(AbstractBaseModel):
    phonenumber = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    receipt_no = models.CharField(max_length=100)

    def __str__(self):
        return self.receipt_no