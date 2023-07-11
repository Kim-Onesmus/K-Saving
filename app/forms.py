from django.forms import ModelForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import Client
from django import forms

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'