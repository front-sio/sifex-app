from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from accounts.models import User
from sifex_system.models import *


class UserForm(ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))

    class Meta:
        model = User 
        fields = ['username', 'first_name', 'last_name', 'email']



class SystemForm(ModelForm):
    class Meta:
        model = SystemPreference 
        fields = ['rate', 'currency', 'exchange_rate']
        



class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))

    class Meta: 
        model = User
        fields = (
            'old_password',
            'new_password1',
            'new_password2',
        )