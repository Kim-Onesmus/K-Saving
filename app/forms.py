from django.forms import ModelForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import Client, My_Plan
from django import forms

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = ['user']
        
        
        
class My_PlanForm(forms.ModelForm):
    class Meta:
        model = My_Plan
        fields = '__all__'