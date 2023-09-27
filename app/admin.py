from django.contrib import admin
from . models import Client, ContactUs, Withdraw, Pay

# Register your models here.
@admin.register(Client)
class ClientTable(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'profile_picture')
    
    
@admin.register(ContactUs)
class ContactUsTable(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'messange')

@amin.register(Pay)
class PayTable(admin.ModelAdmin):
    list_display = ('amount')
    
@admin.register(Withdraw)
class WithdrawTable(admin.ModelAdmin):
    list_display = ('number', 'amount')