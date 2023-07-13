from django.contrib import admin
from . models import Client, ContactUs

# Register your models here.
@admin.register(Client)
class ClientTable(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'profile_picture')
    
    
@admin.register(ContactUs)
class ContactUsTable(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'messange')