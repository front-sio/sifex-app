from django.forms import ModelForm 
from django.forms import formset_factory
from sifex_system.models import Masterawb, Slaveawb, Customer
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
# from django.contrib.auth.models import User
from accounts.models import User
class DateInput(forms.DateInput):
    input_type = 'date'


class MasterForm(ModelForm):
    awb = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    order_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    sender_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    sender_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    sender_city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    sender_comapny = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    sender_country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    receiver_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    receiver_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    receiver_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    receiver_city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    receiver_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    receiver_country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    desc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    freight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    insurance = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    awb_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    awb_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    terms = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    chargable_weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    height = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    width = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    length = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    volume = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    date_received = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    expected_arrival_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    currency = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    custom_value = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    payment_mode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text', }))
    arr_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    arr_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    dlv_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    dlv_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta:
        model = Masterawb
        fields = '__all__'
        
        widgets = {
            'date_received': DateInput(),
            'expected_arrival_date': DateInput()
        }



class MasterCreateForm(ModelForm):
    awb = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    order_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    sender_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    sender_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    sender_city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    sender_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    sender_country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    desc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    freight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    insurance = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    awb_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    awb_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    terms = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    chargable_weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    height = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    width = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    length = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    volume = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    currency = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    custom_value = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    payment_mode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    arr_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    arr_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    dlv_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    dlv_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta:
        model = Masterawb
        fields = '__all__'
        
        widgets = {
            'date_received': DateInput(),
            'expected_arrival_date': DateInput()
        }



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



class SlaveCreateForm(ModelForm):
    awb = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    order_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    receiver_country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    desc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    freight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    insurance = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    awb_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    awb_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    terms = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    chargable_weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    height = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    width = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    length = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    volume = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    currency = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    custom_value = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    payment_mode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    arr_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    arr_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    dlv_pcs = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    dlv_kg = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta:
        model = Slaveawb
        fields = '__all__'
        
        widgets = {
            'date_received': DateInput(),
            'expected_arrival_date': DateInput()
        }



        
class UserRoleForm(ModelForm):
    class Meta:
        model = User
        fields = ('acceptance', 'wharehouse', 'importer', 'accountance', 'management', 'report')



class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data




class InvoiceForm(forms.Form):
    
        # fields = ['customer', 'message']
    customer = forms.CharField(
        label='Cusomter',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Customer/Company Name',
            'rows':1
        })
    )
    customer_email = forms.CharField(
        label='Customer Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'customer@company.com',
            'rows':1
        })
    )
    billing_address = forms.CharField(
        label='Billing Address',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '',
            'rows':1
        })
    )
   

class LineItemForm(forms.Form):
    
    service = forms.CharField(
        label='Service/Product',
        widget=forms.TextInput(attrs={
            'class': 'form-control input',
            'placeholder': 'Service Name'
        })
    )
    description = forms.CharField(
        label='Description',
        widget=forms.TextInput(attrs={
            'class': 'form-control input',
            'placeholder': 'Enter Book Name here',
            "rows":1
        })
    )
    quantity = forms.IntegerField(
        label='Qty',
        widget=forms.TextInput(attrs={
            'class': 'form-control input quantity',
            'placeholder': 'Quantity'
        }) #quantity should not be less than one
    )

    chargable_weight = forms.IntegerField(
        label='Weight',
        widget=forms.TextInput(attrs={
            'class': 'form-control input chargable-weight',
            'placeholder': 'Weight'
        }) #quantity should not be less than one
    )

   

    rate = forms.DecimalField(
        label='Rate $',
        widget=forms.TextInput(attrs={
            'class': 'form-control input rate',
            'placeholder': 'Rate'
        })
    )
    # amount = forms.DecimalField(
    #     disabled = True,
    #     label='Amount $',
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-control input',
    #     })
    # )
    
LineItemFormset = formset_factory(LineItemForm, extra=1)
        


class CustomerForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    class Meta: 
        model = Customer 
        fields = ['name', ]



class FreightForm(forms.ModelForm):
    class Meta:
        model = Freight
        fields = ['freight_rete', 'awb_type']
        widgets = {
            'freight_rete': forms.TextInput(attrs={'class': 'form-control'}),
            'awb_type': forms.Select(attrs={'class': 'form-control'}),
        }

