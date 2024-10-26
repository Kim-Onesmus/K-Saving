from django.contrib import admin
from . models import Client, ContactUs, Withdraw, Pay, MpesaPayment, My_Plan, BaseModel, MpesaCallBacks, MpesaResponseBody, Transaction, Notification

# Register your models here.
@admin.register(Client)
class ClientTable(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email', 'profile_picture')
    
    
@admin.register(ContactUs)
class ContactUsTable(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'messange')


@admin.register(Pay)
class PayTable(admin.ModelAdmin):
    list_display = ('client', 'pay_id', 'amount', 'number', 'created_date', 'created_time')
    
@admin.register(MpesaPayment)
class MpesaPaymentTable(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'middle_name', 'description', 'phone_number', 'amount', 'reference', 'organization_balance', 'type')
 
@admin.register(Withdraw)
class WithdrawTable(admin.ModelAdmin):
    list_display = ('client', 'withdraw_id', 'status', 'number', 'amount', )
    
    
@admin.register(My_Plan)
class My_PlanTable(admin.ModelAdmin):
    list_display = ('plan', 'amount', 'target')

admin.site.register(Notification)

admin.site.register(MpesaResponseBody)
admin.site.register(Transaction)
admin.site.register(MpesaCallBacks)