
from django.forms import ModelForm 
from django.forms import formset_factory
from sifex_system.models import Masterawb, Slaveawb, Customer
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Carousel, About, Team, Banner, Service
# from django.contrib.auth.models import User
from accounts.models import User
class DateInput(forms.DateInput):
    input_type = 'date'

class CarouselForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    carousel_image = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta: 
        model = Carousel 
        fields = ['title', 'description', 'carousel_image']



class AboutForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    carousel_image = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta: 
        model = About 
        fields = ['title', 'description', 'carousel_image']



class TeamForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    carousel_image = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta: 
        model = Team 
        fields = ['title', 'description', 'carousel_image']


class BannerForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    banner_image = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta: 
        model = Banner 
        fields = ['title', 'description', 'carousel_image']


class ServiceForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    icon = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    body = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta: 
        model = Carousel 
        fields = ['title', 'description', 'carousel_image']