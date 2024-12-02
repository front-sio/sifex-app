from django.utils.dateparse import parse_date
from django.conf.urls import handler403, handler404
from django.http import HttpResponseForbidden
import logging
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import ListView
from django.contrib.auth.views import PasswordChangeView
from django.template.loader import get_template
from django.utils.formats import number_format
from django.views import View
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
# from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils.timezone import now as timezone_now
from django.db.models import Sum, F, FloatField, Value
from django.db.models.functions import Cast, Replace
from accounts.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from accounts.decorators import *
from sifex_system.forms import PasswordChangingForm
from sifex_system.models import *
from sifex_system.forms import *
from datetime import datetime as EastAfricaDateTime
import datetime
import pytz
from core.models import *
from .models import Invoice, LineItem, Customer, Attendance, Staff
import pdfkit


# for printing
import os
from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from io import BytesIO
import xlsxwriter
# another approch

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.platypus import Image as PlatypusImage, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

def shorten_string(text, max_length):
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

@login_required
def register_customer(request):
    context = {}
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            ActivityLog.objects.create(
                user=request.user,
                activity_type='CREATE',
                description=f'Registered customer: {customer.name}'
            )
            messages.success(request, 'Customer registered successfully')
            return redirect('display_customer')
    return render(request, 'system/customer/register.html', context)

@login_required
def display_customer(request):
    context = {}
    return render(request, 'system/customer/list.html', context)

@login_required
def console(request):
    today = datetime.date.today()
    week = today - datetime.timedelta(7)
    delivered_this_week = Masterawb.objects.filter(POD=True, deleted=False, date_received__gte=week, date_received__lte=today).order_by('-date_received')
    pcs = Masterawb.objects.all().order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/console/index.html', context)

@login_required
def accept_console(request):
    pcs = Masterawb.objects.filter(accepted=True, deleted=False,)
    slave_pcs = Slaveawb.objects.filter(accepted=True).order_by('-date_received')
    context = {
        'pcs': pcs,
        'slave_pcs': slave_pcs,
    }
    return render(request, 'system/parcels/accept_parcel/index.html', context)

@login_required
def accept_loaded_console(request):
    pcs = Masterawb.objects.filter(loaded=True).order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/accept_parcel/loaded.html', context)

@login_required
def accept_manifested_console(request):
    pcs = Masterawb.objects.filter(manifested=True, deleted=False,).order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/accept_parcel/manifested.html', context)

@login_required
def accept_arrived_console(request):
    pcs = Masterawb.objects.filter(arrived=True).order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/importer/arrived.html', context)

@login_required
def accept_underclearance_console(request):
    pcs = Masterawb.objects.filter(under_clearance=True, deleted=False,).order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/importer/underclearance.html', context)

@login_required
def accept_release_console(request):
    pcs = Masterawb.objects.filter(released=True, deleted=False,).order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/importer/released.html', context)

@login_required
def accept_delivered_console(request):
    pcs = Masterawb.objects.filter(billed=True, deleted=False,).order_by('-date_received').prefetch_related('awb_locations')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/importer/delivered.html', context)

@login_required
def accept_pod_console(request):
    pcs = Masterawb.objects.filter(delivered=True, deleted=False,)
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/importer/pod.html', context)

@login_required
def parcel_update_view(request):
    form = MasterForm()
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = MasterForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.save()
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Updated parcel with AWB: {parcel.awb}'
            )
            return JsonResponse({'awb': parcel.awb, 'sender_name': parcel.sender_name, 'order_number': parcel.order_number, 'id': parcel.id})
    return render(request, 'system/parcels/accept_parcel/parcel_update.html', {'form': form})

@login_required
def accept_parcel(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        awb = request.POST.get('awb')
        order_number = request.POST.get('order_number')
        sender_name = request.POST.get('sender_name')
        sender_address = request.POST.get('sender_address')
        sender_city = request.POST.get('sender_city')
        sender_company = request.POST.get('sender_company')
        sender_tel = request.POST.get('sender_tel')
        sender_country = request.POST.get('sender_country')
        receiver_name = request.POST.get('receiver_name')
        receiver_address = request.POST.get('receiver_address')
        receiver_company = request.POST.get('receiver_company')
        receiver_tel = request.POST.get('receiver_tel')
        receiver_city = request.POST.get('receiver_city')
        receiver_country = request.POST.get('receiver_country')
        desc = request.POST.get('desc')
        freight = request.POST.get('freight')
        freight_rate = request.POST.get('freight_rate')
        insurance = request.POST.get('insurance')
        awb_pcs = request.POST.get('awb_pcs')
        awb_kg = request.POST.get('awb_kg')
        chargable_weight = request.POST.get('chargable_weight')
        terms = request.POST.get('terms')
        volume = request.POST.get('volume')
        height = request.POST.get('height')
        width = request.POST.get('width')
        length = request.POST.get('length')
        currency = request.POST.get('currency')
        date_received = request.POST.get('date_received')
        expected_arrival_date = request.POST.get('expected_arrival_date')
        custom_value = request.POST.get('custom_value')
        payment_mode = request.POST.get('payment_mode')
        awb_type = request.POST.get('awb_type')

        parcel = Masterawb.objects.create(
            awb=awb, 
            order_number=order_number,
            sender_name=sender_name,
            sender_tel=sender_tel,
            awb_type=awb_type,
            sender_address=sender_address,
            sender_city=sender_city,
            sender_company=sender_company,
            sender_country=sender_country,
            receiver_name=receiver_name,
            receiver_tel=receiver_tel,
            receiver_address=receiver_address,
            receiver_city=receiver_city,
            receiver_company=receiver_company,
            receiver_country=receiver_country,
            desc=desc,
            freight=freight,
            freight_rate=freight_rate,
            insurance=insurance,
            awb_pcs=awb_pcs,
            awb_kg=awb_kg,
            chargable_weight=chargable_weight,
            terms=terms,
            volume=volume,
            height=height,
            width=width,
            length=length,
            user=request.user,
            currency=currency,
            date_received=date_received,
            expected_arrival_date=expected_arrival_date,
            custom_value=custom_value,
            payment_mode=payment_mode,
            accepted=True,
        )
        awb_status = MasterStatus.objects.create(master=parcel, user=request.user, status='accepted', date=datetime.datetime.now().date(), time=datetime.datetime.now().time(), terminal='CAN - Guanzhou')
        return JsonResponse({
            'id': parcel.id,
            'awb': parcel.awb,
            'order_number': parcel.order_number,
            'sender_name': parcel.sender_name,
            'sender_tel': parcel.sender_tel,
            'sender_address': parcel.sender_address,
            'sender_city': parcel.sender_city,
            'sender_company': parcel.sender_company,
            'sender_country': parcel.sender_country,
            'receiver_name': parcel.receiver_name,
            'receiver_address': parcel.receiver_address,
            'receiver_tel': parcel.receiver_tel,
            'receiver_city': parcel.receiver_city,
            'receiver_company': parcel.receiver_company,
            'receiver_country': parcel.receiver_country,
            'desc': parcel.desc,
            'freight': parcel.freight,
            'freight_rate': parcel.freight_rate,
            'insurance': parcel.insurance,
            'awb_pcs': parcel.awb_pcs,
            'awb_type': parcel.awb_type,
            'awb_kg': parcel.awb_kg,
            'chargable_weight': parcel.chargable_weight,
            'terms': parcel.terms,
            'volume': parcel.volume,
            'width': parcel.width,
            'height': parcel.height,
            'length': parcel.length,
            'currency': parcel.currency,
            'date_received': parcel.date_received,
            'expected_arrival_date': parcel.expected_arrival_date,
            'custom_value': parcel.custom_value,
            'payment_mode': parcel.payment_mode,
        })

@login_required
def accept_form_view(request):
    form = MasterCreateForm()
    context = {'form': form}
    return render(request, 'system/parcels/accept_parcel/accept.html', context)

@login_required
def accept_form_view(request):
    form = MasterCreateForm()
    context = {'form': form}
    return render(request, 'system/parcels/accept_parcel/accept.html', context)

@login_required
def add_parcel(request):
    if request.method == "POST":
        id = request.POST.get('id')
        parcel_id = Masterawb.objects.get(id=id)
        desc = request.POST.get('desc')
        awb = request.POST.get('awb')
        order_number = request.POST.get('order_number')
        freight = request.POST.get('freight')
        insurance = request.POST.get('insurance')
        awb_pcs = request.POST.get('awb_pcs')
        awb_kg = request.POST.get('awb_kg')
        chargable_weight = request.POST.get('chargable_weight')
        terms = request.POST.get('terms')
        awb_type = request.POST.get('awb_type')
        volume = request.POST.get('volume')
        height = request.POST.get('height')
        width = request.POST.get('width')
        length = request.POST.get('length')
        currency = request.POST.get('currency')
        date_received = request.POST.get('date_received')
        expected_arrival_date = request.POST.get('expected_arrival_date')
        custom_value = request.POST.get('custom_value')
        payment_mode = request.POST.get('payment_mode')

        parcel = Slaveawb.objects.create(
            master=parcel_id,
            desc=desc,
            awb_type=awb_type,
            awb=awb,
            order_number=order_number,
            freight=freight,
            insurance=insurance,
            awb_pcs=awb_pcs,
            awb_kg=awb_kg,
            chargable_weight=chargable_weight,
            terms=terms,
            volume=volume,
            user=request.user,
            height=height,
            width=width,
            length=length,
            currency=currency,
            date_received=date_received,
            expected_arrival_date=expected_arrival_date,
            custom_value=custom_value,
            payment_mode=payment_mode,
        )

        ActivityLog.objects.create(
            user=request.user,
            activity_type='CREATE',
            description=f'Added sub-parcel with AWB: {parcel.awb}'
        )

        return JsonResponse({
            'id': parcel.id,
            'desc': parcel.desc,
            'awb': parcel.awb,
            'order_number': parcel.order_number,
            'freight': parcel.freight,
            'insurance': parcel.insurance,
            'awb_pcs': parcel.awb_pcs,
            'awb_kg': parcel.awb_kg,
            'chargable_weight': parcel.chargable_weight,
            'terms': parcel.terms,
            'volume': parcel.volume,
            'width': parcel.width,
            'height': parcel.height,
            'length': parcel.length,
            'currency': parcel.currency,
            'date_received': parcel.date_received,
            'expected_arrival_date': parcel.expected_arrival_date,
            'custom_value': parcel.custom_value,
            'payment_mode': parcel.payment_mode,
        })

@login_required
def parcel_view(request, pk):
    pc = Masterawb.objects.get(id=pk)
    master_status = pc.master_status.all()
    slave_pcs = pc.slave_master.filter(accepted=True)
    form = MasterForm(instance=pc)
    context = {
        'form': form,
        'master_awb': pc,
        'master_status': master_status,
        'slave_pcs': slave_pcs,
    }
    return render(request, 'system/parcels/importer/view.html', context)

@login_required
def parcel_import(request):
    pcs = Masterawb.objects.filter(departed=True, deleted=False,).order_by('-date_received')
    context = {
        'pcs': pcs,
    }
    return render(request, 'system/parcels/importer/import.html', context)

@login_required
def new_staff(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        accountance = request.POST.get('accountance')
        acceptance = request.POST.get('acceptance')
        wharehouse = request.POST.get('wharehouse')
        management = request.POST.get('management')
        importer = request.POST.get('importer')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if User.objects.filter(username=username).exists():
            messages.success(request, 'Username exists')
            return redirect('new_staff')
        
        acceptance = acceptance == "on"
        accountance = accountance == "on"
        importer = importer == "on"
        wharehouse = wharehouse == "on"
        management = management == "on"

        if password1 == password2:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                acceptance=acceptance,
                accountance=accountance,
                importer=importer,
                wharehouse=wharehouse,
                management=management,
                report=report,
                password=password1,
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='CREATE',
                description=f'Created staff: {user.username}'
            )
            messages.success(request, f'{user.username} account created successfully')
            return redirect('new_staff')
        else:
            messages.success(request, 'Enter the same password as before')
            return redirect('new_staff')
    form = UserRoleForm()
    return render(request, 'system/users/new_staff.html', {'form': form})

class PasswordChange(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('success_password')
    template_name = "system/users/password_change.html"

@login_required
def changepassword(request):
    return render(request, '')

@login_required
def password_success(request):
    return render(request, 'partials/messages/password_success.html')

@login_required
def add_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id)
            awb.accepted = False 
            awb.loaded = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Updated status to {status} for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def add_sub_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id)
            MasterStatus.objects.create(master=awb, user=request.user, status='accepted')
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Updated status to accepted for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
        return redirect('accept_console')

@login_required
def manifested_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.loaded = False 
            awb.manifested = True
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as manifested MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def departed_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.manifested = False 
            awb.departed = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as departed MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def arrived_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.departed = False
            awb.arrived = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as arrived MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def underclearance_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.arrived = False
            awb.under_clearance = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as under clearance MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def released_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.under_clearance = False
            awb.released = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as released MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def payment_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.released = False
            awb.bill = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as bill for payment MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def pod_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        delivered_to = request.POST.get('delivered_to')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.delivered = False
            awb.POD = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                delivered_to=delivered_to,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as POD for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def delivered_master_status(request):
    if request.method == 'POST':
        awb_list = request.POST.getlist('id[]')
        status = request.POST.get('status')
        date = request.POST.get('date')
        time = request.POST.get('time')
        note = request.POST.get('note')
        terminal = request.POST.get('terminal')
        for id in awb_list:
            awb = Masterawb.objects.get(pk=id) 
            awb.invoice_paid = False
            awb.delivered = True 
            awb.save()
            MasterStatus.objects.create(
                master=awb,
                user=request.user,
                status=status,
                date=date,
                time=time,
                note=note,
                terminal=terminal
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='UPDATE',
                description=f'Marked as delivered for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            messages.success(request, f'{awb.sender_name} status updated successfully')
        return redirect('accept_console')

@login_required
def total_master_awb_kg(request):
    today = datetime.date.today()
    month = today - datetime.timedelta(7)
    master_awbs = Masterawb.objects.filter(date_received__gte=month, date_received__lte=today, deleted=False, accepted=True)
   
    finalrep = {}

    def get_awb_type(master_awb):
        return master_awb.awb_type
    awb_type_list = list(set(map(get_awb_type, master_awbs)))

    def get_awb_kg(awb_type):
        awb_kg = 0
        filter_by_awb_type = master_awbs.filter(awb_type=awb_type)
        for item in filter_by_awb_type:
            awb_kg += item.awb_kg
            return awb_kg
    for x in master_awbs:
        for y in awb_type_list:
            finalrep[y] = get_awb_kg(y)
    return JsonResponse({'awb_type_data': finalrep}, safe=False)

@login_required
def total_month_master_awb_kg(request):
    today = datetime.date.today()
    month = today - datetime.timedelta(30)
    master_awbs = Masterawb.objects.filter(date_received__gte=month, deleted=False, date_received__lte=today, POD=True)
    finalrep = {}

    def get_awb_type(master_awb):
        return master_awb.awb_type
    awb_type_list = list(set(map(get_awb_type, master_awbs)))

    def get_awb_kg(awb_type):
        awb_kg = 0
        filter_by_awb_type = master_awbs.filter(awb_type=awb_type)
        for item in filter_by_awb_type:
            awb_kg += item.awb_kg
            return awb_kg
    for x in master_awbs:
        for y in awb_type_list:
            finalrep[y] = get_awb_kg(y)
    return JsonResponse({'awb_type_data': finalrep}, safe=False)

@login_required
def update_slave_arr(request, id):
    if request.method == 'POST':
        slave_awb = Slaveawb.objects.get(pk=id)
        slave_awb.arr_pcs = request.POST.get('arr_pcs')
        slave_awb.arr_kg = request.POST.get('arr_kg')
        slave_awb.save()
        ActivityLog.objects.create(
            user=request.user,
            activity_type='UPDATE',
            description=f'Updated arrival details for SlaveAWB ID: {slave_awb.id}, AWB: {slave_awb.awb}'
        )
        return redirect('parcel_view', slave_awb.master.id)

@login_required
def update_master_arr(request, id):
    if request.method == 'POST':
        master_awb = Masterawb.objects.get(pk=id)
        master_awb.arr_pcs = request.POST.get('arr_pcs')
        master_awb.arr_kg = request.POST.get('arr_kg')
        master_awb.save()
        ActivityLog.objects.create(
            user=request.user,
            activity_type='UPDATE',
            description=f'Updated arrival details for MasterAWB ID: {master_awb.id}, AWB: {master_awb.awb}'
        )
        return redirect('parcel_view', master_awb.id)

@login_required
def update_slave_dlv(request, id):
    if request.method == 'POST':
        slave_awb = Slaveawb.objects.get(pk=id)
        slave_awb.arr_pcs = request.POST.get('arr_pcs')
        slave_awb.arr_kg = request.POST.get('arr_kg')
        slave_awb.save()
        ActivityLog.objects.create(
            user=request.user,
            activity_type='UPDATE',
            description=f'Updated delivery details for SlaveAWB ID: {slave_awb.id}, AWB: {slave_awb.awb}'
        )
        return redirect('parcel_view', slave_awb.master.id)

@login_required
def update_master_dlv(request, id):
    if request.method == 'POST':
        master_awb = Masterawb.objects.get(pk=id)
        master_awb.dlv_pcs = request.POST.get('dlv_pcs')
        master_awb.dlv_kg = request.POST.get('dlv_kg')
        master_awb.save()
        ActivityLog.objects.create(
            user=request.user,
            activity_type='UPDATE',
            description=f'Updated delivery details for MasterAWB ID: {master_awb.id}, AWB: {master_awb.awb}'
        )
        return redirect('parcel_view', master_awb.id)

@login_required
def blog_create_view(request):
    if request.method == "POST":
        title = request.POST.get('title')
        body = request.POST.get('body')
        photo = request.FILES.get('photo')
        if not title:
            messages.error(request, 'Title is required')
            return redirect('blog_create')
        if not body:
            messages.error(request, 'Body is required')
            return redirect('blog_create')
        blog = Post.objects.create(user=request.user, title=title, body=body, photo=photo)
        ActivityLog.objects.create(
            user=request.user,
            activity_type='CREATE',
            description=f'Created blog post: {blog.title}'
        )
        messages.success(request, f'{blog.title} created successfully!')
        return redirect('blogs')
    return render(request, 'system/blog/create.html')

@login_required
def blog_view(request):
    blogs = Post.objects.all()
    context = {
        'blogs': blogs,
    }
    return render(request, 'system/blog/index.html', context)

@login_required
def quotes_view(request):
    quotes = Quote.objects.all()
    context = {
        'quotes': quotes,
    }
    return render(request, 'system/quotes/index.html', context)

@login_required
def users(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'system/users/index.html', context)

@login_required
def delete_user(request, id):
    user = User.objects.get(pk=id)
    user.delete()
    ActivityLog.objects.create(
        user=request.user,
        activity_type='DELETE',
        description=f'Deleted user: {user.username}'
    )
    messages.success(request, f'{user.username} deleted successfully')
    return redirect('users')

@login_required
def on_edit_add_parcel(request):
    if request.method == "POST":
        id = request.POST.get('id')
        master_awb = Masterawb.objects.get(id=id)
        desc = request.POST.get('desc')
        awb = request.POST.get('awb')
        order_number = request.POST.get('order_number')
        freight = request.POST.get('freight')
        insurance = request.POST.get('insurance')
        awb_pcs = request.POST.get('awb_pcs')
        awb_kg = request.POST.get('awb_kg')
        chargable_weight = request.POST.get('chargable_weight')
        terms = request.POST.get('terms')
        awb_type = request.POST.get('awb_type')
        volume = request.POST.get('volume')
        height = request.POST.get('height')
        width = request.POST.get('width')
        length = request.POST.get('length')
        currency = request.POST.get('currency')
        date_received = request.POST.get('date_received')
        expected_arrival_date = request.POST.get('expected_arrival_date')
        custom_value = request.POST.get('custom_value')
        payment_mode = request.POST.get('payment_mode')

        parcel = Slaveawb.objects.create(
            master=master_awb,
            master_awb=master_awb.awb,
            desc=desc,
            awb_type=awb_type,
            awb=awb,
            order_number=order_number,
            freight=freight,
            insurance=insurance,
            awb_pcs=awb_pcs,
            awb_kg=awb_kg,
            chargable_weight=chargable_weight,
            terms=terms,
            volume=volume,
            height=height,
            width=width,
            length=length,
            currency=currency,
            date_received=date_received,
            expected_arrival_date=expected_arrival_date,
            custom_value=custom_value,
            payment_mode=payment_mode,
        )

        ActivityLog.objects.create(
            user=request.user,
            activity_type='CREATE',
            description=f'Added sub-parcel with AWB: {parcel.awb} for MasterAWB: {master_awb.awb}'
        )

        return redirect('parcel_view', master_awb.id)

@login_required
def export_masterawb_pdf_label(request, pk):
    awb = Masterawb.objects.get(id=pk)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Exported PDF label for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
    )
    context = {'awb': awb}
    return render(request, 'system/pdf/export.html', context)

@login_required
def on_edit_add_parcel_view(request, pk):
    form = SlaveCreateForm()
    awb_id = Masterawb.objects.get(id=pk)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Accessed sub-parcel creation view for MasterAWB: {awb_id.awb}'
    )
    ctx = {'master_awb_id': awb_id, 'form': form}
    return render(request, 'system/parcels/importer/add.html', ctx)

@login_required
def location_view(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Accessed location view'
    )
    return render(request, 'location/index.html')

@login_required
def location_search_result(request):
    query = request.GET.get('query')
    if query:
        parcels = Masterawb.objects.filter(
            Q(awb__icontains=query) | Q(order_number__icontains=query)
        )
        if parcels.exists():
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'Found parcel for query: {query}'
            )
            return redirect('location_search_result_found', pk=parcels.first().id)
        else:
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'No parcel found for query: {query}'
            )
            return render(request, 'location/result.html', {'error': 'No parcel found.'})
    else:
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description='No query provided for location search'
        )
        return render(request, 'location/result.html', {'error': 'Please enter a search term.'})

@login_required
def save_location_info(request):
    if request.method == "POST":
        awb_id = request.POST.get("awb_id")
        rack = request.POST.get("rack")
        bay = request.POST.get("bay")
        pcs = request.POST.get("pcs")

        try:
            awb = Masterawb.objects.get(id=awb_id)
            AwbLocation.objects.create(
                awb=awb,
                rack=rack,
                bay=bay,
                pcs=pcs
            )
            ActivityLog.objects.create(
                user=request.user,
                activity_type='CREATE',
                description=f'Saved location info for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
        except Masterawb.DoesNotExist:
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'Failed to find MasterAWB for location info save, AWB ID: {awb_id}'
            )
            return redirect('location_search')

        return redirect('location_search_result_found', pk=awb.id)
    else:
        return redirect('location_search')

@login_required
def location_search_process(request):
    query = request.GET.get('query')
    if query:
        try:
            master_awb = Masterawb.objects.get(awb=query)
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'Found parcel for query: {query}'
            )
            return redirect('location_search_result_found', pk=master_awb.id)
        except Masterawb.DoesNotExist:
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'No parcel found for query: {query}'
            )
            return render(request, 'location/result.html', {'error': 'No parcel found.'})
    else:
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description='No query provided for location search'
        )
        return render(request, 'location/result.html', {'error': 'Please enter a search term.'})

@login_required
def location_search_result_found(request, pk):
    master_awb = get_object_or_404(Masterawb, id=pk)
    locations = AwbLocation.objects.filter(awb=master_awb)

    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Found locations for MasterAWB ID: {master_awb.id}, AWB: {master_awb.awb}'
    )

    context = {
        'master_awb': master_awb,
        'locations': locations
    }
    return render(request, 'location/result.html', context)

@login_required
def invoice_detail(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        line_items = invoice.invoces_line.all()
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Viewed invoice details for Invoice ID: {invoice.id}'
        )
        context = {
            'invoice': invoice,
            'line_items': line_items
        }
        return render(request, 'invoice/invoice_detail.html', context)
    except Invoice.DoesNotExist:
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Invoice not found for Invoice ID: {invoice_id}'
        )
        return HttpResponseNotFound("Invoice not found")




class InvoiceListView(View):
    def get(self, request, *args, **kwargs):
        sort_by = request.GET.get('sort_by', 'id')
        sort_order = request.GET.get('order', 'asc')
        
        # Determine the sorting order
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        
        invoices = Invoice.objects.filter(deleted=False).order_by(sort_by)
        
        ActivityLog.objects.create(
            user=self.request.user,
            activity_type='READ',
            description='Viewed list of invoices'
        )
        
        context = {
            "invoices": invoices,
            "sort_by": request.GET.get('sort_by', 'id'),
            "sort_order": sort_order,
        }
        
        return render(self.request, 'invoice/invoice-list.html', context)

    def post(self, request):
        invoice_ids = request.POST.getlist("invoice_id")
        invoice_ids = list(map(int, invoice_ids))

        update_status_for_invoices = request.POST['status']
        update_detail_for_invoice = request.POST['invoice_detail']
        invoices = Invoice.objects.filter(id__in=invoice_ids)

        # Define East Africa Time Zone
        eat_timezone = pytz.timezone('Africa/Nairobi')

        for invoice in invoices:
            awb = invoice.awb
            old_status = invoice.status  # Store the old status before changing it
            
            if update_status_for_invoices == 'paid':
                invoice.status = 'paid'
                invoice.invoice_detail = update_detail_for_invoice
                # Set date_of_payment to the current time in EAT
                invoice.date_of_payment = EastAfricaDateTime.now(eat_timezone)
                awb.invoice_generated = False
                awb.billed = True
                MasterStatus.objects.create(
                    master=awb,
                    user=request.user,
                    status='invoice paid',
                    date=timezone_now().date(),
                    time=timezone_now().time(),
                    terminal='DAR - Dar es salaam',
                    note='Invoice marked as paid'
                )
                ActivityLog.objects.create(
                    user=request.user,
                    activity_type='UPDATE',
                    description=f'Marked invoice as paid for Invoice ID: {invoice.id}, AWB: {awb.awb}'
                )
            elif update_status_for_invoices == 'credited':
                invoice.status = 'credited'
                invoice.invoice_detail = update_detail_for_invoice
                # Set date_of_payment to the current time in EAT
                invoice.date_of_payment = EastAfricaDateTime.now(eat_timezone)
                awb.billed = True
                awb.invoice_generated = False
                MasterStatus.objects.create(
                    master=awb,
                    user=request.user,
                    status='invoice credited',
                    date=timezone_now().date(),
                    time=timezone_now().time(),
                    terminal='DAR - Dar es salaam',
                    note='Invoice marked as credited'
                )
                ActivityLog.objects.create(
                    user=request.user,
                    activity_type='UPDATE',
                    description=f'Marked invoice as credited for Invoice ID: {invoice.id}, AWB: {awb.awb}'
                )
            
            # Create an InvoiceHistory entry
            InvoiceHistory.objects.create(
                invoice_id=invoice.id,
                awb=invoice.awb.awb,
                customer=invoice.customer,
                pcs=invoice.awb.awb_pcs,
                weight_kg=invoice.awb.awb_kg,
                origin=invoice.awb.awb_type,
                total_amount_tzs=invoice.total_amount_tzs,
                status=old_status,  # Store the old status in history
                action=f'{old_status} -> {invoice.status}',  # Record the status change
                performed_by=request.user,
                note=f'Invoice status changed from {old_status} to {invoice.status}'
            )

            awb.save()
            invoice.save()

        return redirect('invoice-list')


@login_required
def createInvoice(request, pk):
    awb = Masterawb.objects.get(id=pk)
    if request.method == 'POST':
        customer = request.POST.get('customer')
        customer_phone = request.POST.get('customer_phone')
        origin = request.POST.get('origin')
        billing_address = request.POST.get('billing_address')
        date = request.POST.get('date')
        due_date = request.POST.get('due_date')
        invoice = Invoice.objects.create(
            customer=customer,
            awb=awb,
            origin=origin,
            customer_phone=customer_phone,
            billing_address=billing_address,
            date=date,
            due_date=due_date,
            user=request.user
        )

        total_tz = 0
        total_usd = 0

        user_preferences = SystemPreference.objects.all()[:1]
        exchange_rates = 0
        for exch in user_preferences:
            exchange_rates = exch.exchange_rate

        service = request.POST.get('service')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        chargable_weight = request.POST.get('chargable_weight')
        rate = request.POST.get('rate')
        if service and description and quantity and rate and chargable_weight:
            amount_tz = float(rate) * float(chargable_weight) * float(exchange_rates)
            total_tz += amount_tz
            amount_usd = float(rate) * float(chargable_weight)
            total_usd += amount_usd
            LineItem.objects.create(
                customer=invoice,
                service=service,
                description=description,
                tracking_key=awb.awb,
                quantity=quantity,
                chargable_weight=chargable_weight,
                rate=rate,
                amount_tz=amount_tz,
                amount_usd=amount_usd
            )
            invoice.total_amount_tzs = total_tz
            invoice.total_amount_usd = total_usd
            invoice.save()
            awb.bill = False
            awb.invoice_generated = True
            awb.save()
            ActivityLog.objects.create(
                user=request.user,
                activity_type='CREATE',
                description=f'Created invoice for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
            )
            return redirect('invoice-list')

    context = {
        "title": "Sifex Invoice Generator",
        "awb": awb,
    }
    return render(request, 'invoice/invoice-create.html', context)

@login_required
def view_PDF(request, id=None):
    invoice = get_object_or_404(Invoice, id=id)
    lineitem = invoice.lineitem_set.all()

    invoice_total_usd = sum(item.amount_usd for item in lineitem)
    invoice_total_tzs = sum(item.amount_tz for item in lineitem)

    context = {
        "company": {
            "name": "SIFEX COURIER COMPANY LIMITED",
            "address": """Dar es salaam, Ilala, 
            Kipawa street-Plot No 236 Zakhem Plaza
            1st Floor
            """,
            "phone": "(+255) 688 930 963",
            "TIN": "142-996-014",
        },
        "invoice_id": invoice.id,
        "invoice_origin": invoice.origin,
        "invoice_total": invoice_total_usd,
        "invoice_total_usd": invoice_total_usd,
        "invoice_total_tzs": invoice_total_tzs,
        "customer": invoice.customer,
        "customer_email": invoice.customer_email,
        "date": invoice.date,
        "due_date": invoice.due_date,
        "billing_address": invoice.billing_address,
        "lineitem": lineitem,
    }
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Viewed PDF for Invoice ID: {invoice.id}'
    )
    return render(request, 'invoice/pdf_template.html', context)

@login_required
def generate_pdf(request):
    pcs = Masterawb.objects.filter(deleted=False)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="manifested_awb.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 750, "Manifested AWB")

    data = [["RECEIVER NAME", "AWB", "Order number", "AWB PCS", "AWB KG"]]
    for pc in pcs:
        data.append([pc.receiver_name, pc.awb, pc.order_number, pc.awb_pcs, pc.awb_kg])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table.wrapOn(p, 800, 600)
    table.drawOn(p, 50, 600)

    p.showPage()
    p.save()

    buffer.seek(0)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Generated PDF for manifested AWBs'
    )
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def generate_spreadsheet(request):
    pcs = Masterawb.objects.filter(deleted=False)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="manifested_awb.xlsx"'

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    headers = ["RECEIVER NAME", "AWB", "Order number", "AWB PCS", "AWB KG"]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    for row_num, pc in enumerate(pcs, start=1):
        worksheet.write(row_num, 0, pc.receiver_name)
        worksheet.write(row_num, 1, pc.awb)
        worksheet.write(row_num, 2, pc.order_number)
        worksheet.write(row_num, 3, pc.awb_pcs)
        worksheet.write(row_num, 4, pc.awb_kg)

    workbook.close()
    output.seek(0)

    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Generated spreadsheet for manifested AWBs'
    )
    return HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@login_required
def change_status(request):
    return redirect('invoice-list')

def view_404(request, *args, **kwargs):
    return redirect('invoice-list')

@login_required
def delete_awb(request, id):
    awb = get_object_or_404(Masterawb, pk=id)
    awb.deleted = True
    awb.save()

    ActivityLog.objects.create(
        user=request.user,
        activity_type='DELETE',
        description=f'Marked AWB ID: {awb.id} as deleted'
    )
    messages.success(request, f'AWB {awb.awb} marked as deleted successfully')
    return redirect('accept_console')


@login_required
def delete_invoice(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    awb = invoice.awb
    invoice.deleted = True
    invoice.save()
    
    if awb.billed:
        awb.billed = False
        awb.bill = True
    elif awb.invoice_generated:
        awb.invoice_generated = False
        awb.bill = True
    awb.save()

    ActivityLog.objects.create(
        user=request.user,
        activity_type='DELETE',
        description=f'Marked Invoice ID: {invoice.id}, Customer: {invoice.customer} as deleted'
    )
    messages.success(request, f'Invoice {invoice.customer} marked as deleted successfully')
    return redirect('invoice-list')


@login_required
def awb_edit(request, pk):
    master_awb = Masterawb.objects.get(id=pk)
    
    if request.method == 'POST':
        # Store old values
        old_values = {
            'awb': master_awb.awb,
            'order_number': master_awb.order_number,
            'sender_name': master_awb.sender_name,
            'sender_address': master_awb.sender_address,
            'sender_city': master_awb.sender_city,
            'sender_tel': master_awb.sender_tel,
            'sender_country': master_awb.sender_country,
            'receiver_name': master_awb.receiver_name,
            'receiver_address': master_awb.receiver_address,
            'receiver_tel': master_awb.receiver_tel,
            'receiver_city': master_awb.receiver_city,
            'receiver_country': master_awb.receiver_country,
            'desc': master_awb.desc,
            'freight': master_awb.freight,
            'insurance': master_awb.insurance,
            'awb_pcs': master_awb.awb_pcs,
            'awb_kg': master_awb.awb_kg,
            'chargable_weight': master_awb.chargable_weight,
            'terms': master_awb.terms,
            'volume': master_awb.volume,
            'height': master_awb.height,
            'width': master_awb.width,
            'length': master_awb.length,
            'currency': master_awb.currency,
            'date_received': master_awb.date_received,
            'expected_arrival_date': master_awb.expected_arrival_date,
            'custom_value': master_awb.custom_value,
            'payment_mode': master_awb.payment_mode,
            'awb_type': master_awb.awb_type,
        }

        # Store new values
        new_values = {
            'awb': request.POST.get('awb'),
            'order_number': request.POST.get('order_number'),
            'sender_name': request.POST.get('sender_name'),
            'sender_address': request.POST.get('sender_address'),
            'sender_city': request.POST.get('sender_city'),
            'sender_tel': request.POST.get('sender_tel'),
            'sender_country': request.POST.get('sender_country'),
            'receiver_name': request.POST.get('receiver_name'),
            'receiver_address': request.POST.get('receiver_address'),
            'receiver_tel': request.POST.get('receiver_tel'),
            'receiver_city': request.POST.get('receiver_city'),
            'receiver_country': request.POST.get('receiver_country'),
            'desc': request.POST.get('desc'),
            'freight': request.POST.get('freight'),
            'insurance': request.POST.get('insurance'),
            'awb_pcs': request.POST.get('awb_pcs'),
            'awb_kg': request.POST.get('awb_kg'),
            'chargable_weight': request.POST.get('chargable_weight'),
            'terms': request.POST.get('terms'),
            'volume': request.POST.get('volume'),
            'height': request.POST.get('height'),
            'width': request.POST.get('width'),
            'length': request.POST.get('length'),
            'currency': request.POST.get('currency'),
            'date_received': request.POST.get('date_received'),
            'expected_arrival_date': request.POST.get('expected_arrival_date'),
            'custom_value': request.POST.get('custom_value'),
            'payment_mode': request.POST.get('payment_mode'),
            'awb_type': request.POST.get('awb_type'),
        }

        # Update the Masterawb instance
        changes = []
        for field, new_value in new_values.items():
            old_value = old_values[field]
            if old_value != new_value:
                setattr(master_awb, field, new_value)
                changes.append(f"Field '{field}' changed from '{old_value}' to '{new_value}'")

        # Check for changes and save
        if changes:
            change_summary = "\n".join(changes)
            remark = request.POST.get('remark')

            if not remark:
                # Return error if no remark is provided
                return render(request, 'system/parcels/importer/view.html', {
                    'form': MasterForm(instance=master_awb),
                    'master_awb': master_awb,
                    'error': 'You must provide a remark for the changes.',
                })

            # Save the changes and log the history
            master_awb.save()
            AwbHistory.objects.create(
                master_awb=master_awb,
                changed_by=request.user,
                change_summary=change_summary,
                remark=remark
            )

        return redirect('parcel_view', master_awb.id)


    


@login_required
def generate_invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    lineitems = LineItem.objects.filter(customer=invoice)

    def shorten_text(text, max_length):
        if len(text) > max_length:
            return text[:max_length-3] + '...'
        return text

    def format_currency(value):
        """Format the currency value preserving decimals."""
        return f"{value:,.2f}"  # Preserve two decimal places

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    logo_path = os.path.join(settings.STATIC_ROOT, 'assets/img/sifex/logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, 720, width=140, height=50, mask='auto')
    else:
        p.drawString(40, 720, "Logo not found")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(200, 750, "SIFEX COURIER COMPANY LIMITED")
    p.setFont("Helvetica", 10)
    p.drawString(200, 735, "Plot No. 658 KUrasini, Mgulani, Minazini Street,")
    p.drawString(200, 720, "Near Uhasibu College Dar es salaam")
    p.drawString(200, 705, "(+255) 688 930 963")
    p.drawString(200, 690, "TIN: 142-996-014")

    p.saveState()
    p.setFont("Helvetica-Bold", 16)
    if invoice.status == 'paid':
        p.setFillColorRGB(0, 1, 0)
        p.translate(500, 700)
        p.rotate(45)
        p.drawString(0, 0, "PAID")
    elif invoice.status == 'credited':
        p.setFillColorRGB(0, 0, 1)
        p.translate(500, 700)
        p.rotate(45)
        p.drawString(0, 0, "CREDITED")
    else:
        p.setFillColorRGB(1, 0, 0)
        p.translate(500, 700)
        p.rotate(45)
        p.drawString(0, 0, "UNPAID")
    p.restoreState()

    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, 670, "INVOICE TO:")
    p.setFont("Helvetica", 10)
    p.drawString(40, 655, invoice.customer)
    p.drawString(40, 640, invoice.billing_address)
    p.drawString(40, 625, invoice.customer_phone)
    if invoice.customer_email:
        p.drawString(40, 610, invoice.customer_email)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, 580, f"Invoice #{invoice.id}")
    p.setFont("Helvetica", 10)
    p.drawString(40, 565, f"Date of Invoice: {invoice.date}")
    p.drawString(40, 550, f"Due Date: {invoice.due_date}")

    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.wordWrap = 'CJK'

    data = [["#", "AWB", "RATE", "ORIGIN", "QUANTITY", "WEIGHT", "AMOUNT IN TZS", "AMOUNT IN USD"]]
    for idx, item in enumerate(lineitems, start=1):
        data.append([
            str(idx),
            item.service,
            f"${format_currency(item.rate)}",  # Preserve decimal places in rate
            shorten_text(invoice.origin or '', 8),
            str(item.quantity),
            str(item.chargable_weight),
            f"Tzs {format_currency(item.amount_tz)}",  # Preserve decimal places for amount in TZS
            f"${format_currency(item.amount_usd)}"  # Preserve decimal places for amount in USD
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (0, -1), colors.green),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),
        ('BACKGROUND', (-2, 1), (-1, -1), colors.red),
        ('TEXTCOLOR', (-2, 1), (-1, -1), colors.whitesmoke),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    table.wrapOn(p, 800, 600)
    table.drawOn(p, 30, 350)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, 300, f"SUBTOTAL: ${format_currency(invoice.total_amount_usd)}")
    p.drawString(40, 285, f"TOTAL IN USD: ${format_currency(invoice.total_amount_usd)}")
    p.drawString(40, 270, f"TOTAL IN TZS: Tzs {format_currency(invoice.total_amount_tzs)}")

    p.drawString(40, 240, "PAYMENT INSTRUCTION:")
    p.setFont("Helvetica", 10)
    p.drawString(40, 225, "BANK NAME: NMB BANK, AIRPORT BRANCH")
    p.drawString(40, 210, "ACCOUNT NAME: SIFEX COURIER SERVICES COMPANY LTD")
    p.drawString(40, 195, "ACCOUNT NUMBER: 23010064562")
    p.drawString(40, 180, "TIGO LIPA NAMBA: 5026775")
    p.drawString(40, 165, "ACCOUNT NAME: SIFEX COURIER SERVICES COMPANY LTD")
    p.drawString(40, 150, "CURRENCY: TZS")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, 120, "TERMS AND CONDITIONS:")
    p.setFont("Helvetica", 10)
    p.drawString(40, 105, "A finance charge of 1.5% will be made on unpaid balances after 30 days.")

    p.showPage()
    p.save()

    buffer.seek(0)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Generated PDF for Invoice ID: {invoice.id}'
    )

    # Set the response to download the file
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.id}.pdf"'
    return response



@login_required
def invoice_generation(request):
    pcs = Masterawb.objects.filter(bill=True, deleted=False)
    exchange_rate = SystemPreference.objects.first()
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Accessed invoice generation page'
    )
    ctx = {
        'pcs': pcs,
        'exchange_rate': exchange_rate,
    }
    return render(request, 'invoice/generate_invoice.html', ctx)

@login_required
def list_of_delivered_awb(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of delivered AWBs'
    )
    return render(request, 'system/reports/delivered-goods.html', {})


@login_required
def list_of_undelivered_awb(request):
    # Tunatafuta AWBs ambazo hazijafika "delivered" lakini zina status zote
    undelivered_awbs = Masterawb.objects.filter(
        delivered=False,  # Hazijafika delivered
        master_status__status__in=['arrival', 'underclearance', 'released', 'bill', 'invoice paid']
    ).annotate(
        status_count=Count('master_status__status', filter=Q(master_status__status__in=['arrival', 'underclearance', 'released', 'bill', 'invoice paid']))
    ).filter(
        status_count=5  # Zina hizi status zote 5
    ).order_by('-date_received')

    # Rekodi kuwa mtumiaji amefungua ukurasa huu
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of undelivered AWBs with status arrival, underclearance, released, bill, and invoice paid'
    )
    
    return render(request, 'system/reports/undelivered-goods.html', {
        'undelivered_awbs': undelivered_awbs
    })

@login_required
def list_of_paid_awb(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of paid AWBs'
    )
    return render(request, 'system/reports/paid-goods.html', {})

@login_required
def list_of_unpaid_awb(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of unpaid AWBs'
    )
    return render(request, 'system/reports/unpaid-goods.html', {})

@login_required
def list_of_credited_awb(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of credited AWBs'
    )
    return render(request, 'system/reports/credited-goods.html', {})

@login_required
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        if not name:
            messages.error(request, 'Name field is required')
            return render(request, 'system/customer/create.html', {})
        if not phone:
            messages.error(request, 'Phone number field is required')
            return render(request, 'system/customer/create.html', {})
        customer = Customer.objects.create(name=name, user=request.user, phone=phone, address=address, city=city, country=country)
        ActivityLog.objects.create(
            user=request.user,
            activity_type='CREATE',
            description=f'Added customer: {customer.name}'
        )
        messages.success(request, f'Customer {customer.name} added successfully')
        return redirect('customers-list')
    return render(request, 'system/customer/create.html', {})

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of customers'
    )
    return render(request, 'system/customer/index.html', {'customers': customers})

@login_required
def delivered_report(request):
    pcs = None
    total_undelivered = 0
    total_kg = 0
    total_freight = 0  # Initialize total freight

    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')

        # Filter for delivered pcs within the date range
        pcs = Masterawb.objects.filter(
            deleted=False,
            delivered=True,
            date_received__range=[date_from, date_to]
        )

        total_undelivered = pcs.count()  # Total delivered AWBs
        total_kg = pcs.aggregate(Sum('awb_kg'))['awb_kg__sum'] or 0  # Total kg of delivered AWBs

    return render(request, 'system/reports/dlv-reports.html', {
        'pcs': pcs,
        'total_undelivered': total_undelivered,
        'total_kg': total_kg,
    })


@login_required
@login_required
def undelivered_report(request):
    pcs = None
    total_undelivered = 0
    total_kg = 0

    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')

        # Filter for undelivered pcs within the date range and specific statuses
        pcs = Masterawb.objects.filter(
            delivered=False,  # AWBs that are not yet delivered
            date_received__range=[date_from, date_to]  # Date range filter
        ).filter(
            master_status__status__in=['arrived', 'under clearance', 'released', 'invoice credited', 'invoice paid']  # Status filter
        ).distinct()

        # Calculate total undelivered count and total weight
        total_undelivered = pcs.count()  # Total undelivered AWBs
        total_kg = pcs.aggregate(Sum('awb_kg'))['awb_kg__sum'] or 0  # Total kg of undelivered AWBs

    return render(request, 'system/reports/undlv-reports.html', {
        'pcs': pcs,
        'total_undelivered': total_undelivered,
        'total_kg': total_kg,
    })



@login_required
def paid_report(request):
    invoices = []
    total_invoices = 0
    total_amount_tzs = 0

    if request.method == "POST":
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        invoices = Invoice.objects.filter(date_of_payment__gte=date_from, date_of_payment__lte=date_to, status='paid')
        
        total_invoices = invoices.count()
        total_amount_tzs = invoices.aggregate(total=Sum('total_amount_tzs'))['total'] or 0

        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Viewed paid report from {date_from} to {date_to}'
        )
    
    context = {
        'invoices': invoices,
        'total_invoices': total_invoices,
        'total_amount_tzs': total_amount_tzs,
    }
    return render(request, 'system/reports/paid-reports.html', context)


@login_required
def freight_report(request):
    if not request.user.management:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    pcs = None
    total_freight = 0
    total_chargable_weight = 0

    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')

        # Filter AWBs within the date range
        pcs = Masterawb.objects.filter(
            date_received__range=[date_from, date_to]
        )

        # Replace '$' with an empty string in the 'freight' field and cast it to Float for summation
        pcs = pcs.annotate(
            cleaned_freight=Cast(Replace('freight', Value('$'), Value('')), FloatField()),
            cleaned_chargable_weight=Cast('chargable_weight', FloatField())  # Cast chargable_weight to Float
        )

        # Sum the cleaned 'freight' field
        total_freight = pcs.aggregate(total_freight=Sum('cleaned_freight'))['total_freight'] or 0

        # Sum the cleaned 'chargable_weight' field
        total_chargable_weight = pcs.aggregate(total_chargable_weight=Sum('cleaned_chargable_weight'))['total_chargable_weight'] or 0

    return render(request, 'system/reports/freight-reports.html', {
        'pcs': pcs,
        'total_freight': total_freight,
        'total_chargable_weight': total_chargable_weight,
    })




@login_required
def credited_report(request):
    invoices = []
    if request.method == "POST":
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        invoices = Invoice.objects.filter(date_of_payment__gte=date_from, date_of_payment__lte=date_to, status='credited')
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Viewed credited report from {date_from} to {date_to}'
        )
    context = {'invoices': invoices}
    return render(request, 'system/reports/credited-reports.html', context)

@login_required
def unpaid_report(request):
    invoices = []
    total_invoices = 0
    total_amount_usd = 0
    total_amount_tzs = 0

    if request.method == "POST":
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        invoices = Invoice.objects.filter(date_of_payment__gte=date_from, date_of_payment__lte=date_to, status='unpaid')
        
        total_invoices = invoices.count()
        total_amount_usd = invoices.aggregate(total_usd=Sum('total_amount_usd'))['total_usd'] or 0
        total_amount_tzs = invoices.aggregate(total_tzs=Sum('total_amount_tzs'))['total_tzs'] or 0

        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Viewed unpaid report from {date_from} to {date_to}'
        )
    
    context = {
        'invoices': invoices,
        'total_invoices': total_invoices,
        'total_amount_usd': total_amount_usd,
        'total_amount_tzs': total_amount_tzs,
    }
    return render(request, 'system/reports/unpaid-reports.html', context)




@login_required
def credited_report(request):
    invoices = []
    total_invoices = 0
    total_amount_usd = 0
    total_amount_tzs = 0

    if request.method == "POST":
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        invoices = Invoice.objects.filter(date__gte=date_from, date__lte=date_to, status='credited')
        
        total_invoices = invoices.count()
        total_amount_usd = invoices.aggregate(total_usd=Sum('total_amount_usd'))['total_usd'] or 0
        total_amount_tzs = invoices.aggregate(total_tzs=Sum('total_amount_tzs'))['total_tzs'] or 0

        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Viewed credited report from {date_from} to {date_to}'
        )
    
    context = {
        'invoices': invoices,
        'total_invoices': total_invoices,
        'total_amount_usd': total_amount_usd,
        'total_amount_tzs': total_amount_tzs,
    }
    return render(request, 'system/reports/credited-reports.html', context)


@login_required
def check_staff(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed staff check-in page'
    )
    return render(request, 'system/attendance/check_staff.html')

@login_required
def check_staff_by_code(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Checked staff by code'
    )
    return render(request, 'system/attendance/check_staff_by_code.html')

@login_required
def check_staff_id(request):
    if request.method == 'POST':
        staffcode = request.POST.get('staffcode')
        result = None
        if Staff.objects.filter(code_number=staffcode).exists():
            staff = Staff.objects.get(code_number=staffcode)
            item = {
                'pk': staff.pk,
                'code_number': staff.code_number,
                'name': staff.name,
            }
            data = item
            result = data
        else:
            result = 'not found'
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description=f'Checked staff ID for staff code: {staffcode}'
        )
        return JsonResponse({'data': result})
    return JsonResponse({})

@login_required
def mark_attendance_in(request):
    if request.method == "POST":
        staffcode = request.POST.get('staffcode')
        staff = Staff.objects.get(code_number=staffcode)
        result = None 
        if Attendance.objects.filter(date=date, staff=staff).exists():
            attendances = Attendance.objects.filter(staff=staff)
            for attendance in attendances:
                if attendance.out_time:
                    result = f'Sorry already marked out'
                    return JsonResponse({'data': result})
                else:
                    attendance.out_time = now.time()
                    attendance.present = True
                    attendance.save()
                    ActivityLog.objects.create(
                        user=request.user,
                        activity_type='UPDATE',
                        description=f'Marked attendance out for staff: {staff.name}'
                    )
                    result = 'signed out successfully'
                    return JsonResponse({'data': result})
        else:
            attendance = Attendance.objects.create(staff=staff, in_time=now.time())
            item = {
                'pk': attendance.pk,
                'in_time': attendance.in_time,
                'date': attendance.date,
                'staff': staff.name,
            }
            data = item
            result = data
            ActivityLog.objects.create(
                user=request.user,
                activity_type='CREATE',
                description=f'Marked attendance in for staff: {staff.name}'
            )
            return JsonResponse({'data': result})
    return JsonResponse({})

@login_required
def mark_attendance_out(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='UPDATE',
        description='Marked attendance out'
    )
    return render(request, 'system/attendance/take_attendance.html', {})

@login_required
def filter_attendance(request):
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Filtered attendance records'
    )
    return render(request, 'system/attendance/filter.html', {})

@login_required
def list_attendance(request):
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')
    attendances = Attendance.objects.filter(date__gte=date_from, date__lte=date_to)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Viewed attendance list from {date_from} to {date_to}'
    )
    return render(request, 'system/attendance/index.html', {'attendances': attendances})

@login_required
def register_staff(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        code_number = request.POST.get('code_number')
        role = request.POST.get('role')
        if not name:
            messages.error(request, 'Name field is required')
            return render(request, 'system/staff/create.html', {})
        if not phone:
            messages.error(request, 'Phone number field is required')
            return render(request, 'system/staff/create.html', {})
        if not code_number:
            messages.error(request, 'Code number field is required')
            return render(request, 'system/staff/create.html', {})
        staff = Staff.objects.create(name=name, user=request.user, phone=phone, address=address, city=city, country=country, code_number=code_number, role=role)
        ActivityLog.objects.create(
            user=request.user,
            activity_type='CREATE',
            description=f'Registered staff: {staff.name}'
        )
        messages.success(request, f'Staff {staff.name} registered successfully')
        return redirect('staff-list')
    return render(request, 'system/staff/create.html', {})

@login_required
def staff_list(request):
    staff = Staff.objects.all()
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Viewed list of staff'
    )
    return render(request, 'system/staff/index.html', {'staff': staff})







@login_required
def print_label(request, pk):
    awb = get_object_or_404(Masterawb, pk=pk)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(4 * inch, 6 * inch))

    p.setFont("Helvetica", 10)
    p.setLineWidth(1)
    p.rect(10, 10, 4 * inch - 20, 6 * inch - 20)
    
    logo_path = os.path.join(settings.STATIC_ROOT, 'assets/img/sifex/logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 20, 330, width=0.8 * inch, height=0.5 * inch, mask='auto')
    else:
        p.drawString(20, 330, "Logo not found")
    
    barcode_value = awb.awb
    barcode = code128.Code128(barcode_value, barHeight=10*mm, barWidth=0.5*mm)
    barcode.drawOn(p, 20, 390)
    p.drawString(100, 380, barcode_value)

    def shorten_text(text, max_length):
        if len(text) > max_length:
            return text[:max_length-3] + '...'
        return text

    info = [
        ("Sender Name:", shorten_text(awb.sender_name or '', 30)),
        ("Sender Address:", shorten_text(awb.sender_address or '', 20)),
        ("Sender Company:", shorten_text(awb.sender_company or '', 26)),
        ("Sender Phone:", shorten_text(awb.sender_tel or '', 30)),
        ("Receiver Name:", shorten_text(awb.receiver_name or '', 30)),
        ("Receiver Address:", shorten_text(awb.receiver_address or '', 20)),
        ("Receiver Company:", shorten_text(awb.receiver_company or '', 26)),
        ("Receiver Phone:", shorten_text(awb.receiver_tel or '', 30)),
        ("Payment type:", shorten_text(awb.payment_mode or '', 30)),
        ("Number of pieces:", str(awb.awb_pcs) or ''),
        ("Chargeable weight:", f"{awb.awb_kg} kg" if awb.awb_kg else ''),
        ("Volume:", shorten_text(awb.volume or '', 30)),
        ("Desc:", shorten_text(awb.desc or '', 30)),
        ("Custom value", shorten_text(awb.custom_value or '', 25)),
        ("RECEIVER'S SIGNATURE:",  '')
    ]

    y = 300
    for label, value in info:
        p.drawString(20, y, label)
        p.drawString(130, y, value)
        y -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Printed label for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
    )
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def search_parcel(request):
    query = request.GET.get('query')
    if query:
        parcels = Masterawb.objects.filter(
            Q(awb__icontains=query) | Q(order_number__icontains=query)
        )
        if parcels.exists():
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'Searched parcel with query: {query}'
            )
            return redirect('search_found', pk=parcels.first().id)
        else:
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'No parcel found for query: {query}'
            )
            return render(request, 'system/parcels/search/search_results.html', {'error': 'No parcel found.'})
    else:
        ActivityLog.objects.create(
            user=request.user,
            activity_type='READ',
            description='No query provided for parcel search'
        )
        return render(request, 'system/parcels/search/search_results.html', {'error': 'Please enter a search term.'})




@login_required
def search_found(request, pk):
    pc = Masterawb.objects.get(id=pk)
    master_status = pc.master_status.all()
    slave_pcs = pc.slave_master.filter(accepted=True)
    form = MasterForm(instance=pc)
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Found parcel details for MasterAWB ID: {pc.id}, AWB: {pc.awb}'
    )
    context = {
        'form': form,
        'master_awb': pc,
        'master_status': master_status,
        'slave_pcs': slave_pcs,
    }
    return render(request, 'system/parcels/search/search_found.html', context)

# Sales report views
@login_required
def generate_sales_report(request):
    if request.method == "POST":
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        invoice_detail = request.POST.get('invoice_detail')

        if date_from and date_to and invoice_detail:
            ActivityLog.objects.create(
                user=request.user,
                activity_type='READ',
                description=f'Generated sales report from {date_from} to {date_to} for {invoice_detail}'
            )
            return redirect(f'{invoice_detail}_sales_report', date_from=date_from, date_to=date_to)
    
    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description='Accessed sales report generation form'
    )
    return render(request, 'system/reports/generate_sales_report_form.html')

def sales_report_view(request, date_from, date_to, payment_method):
    date_from = parse_date(date_from)
    date_to = parse_date(date_to)

    filtered_invoices = Invoice.objects.filter(date__range=[date_from, date_to], invoice_detail=payment_method)
    
    total_sales_tzs = LineItem.objects.filter(customer__in=filtered_invoices).aggregate(total=Sum('amount_tz'))['total'] or 0
    total_sales_usd = LineItem.objects.filter(customer__in=filtered_invoices).aggregate(total=Sum('amount_usd'))['total'] or 0

    context = {
        'invoices': filtered_invoices,
        'total_sales_tzs': total_sales_tzs,
        'total_sales_usd': total_sales_usd,
        'date_from': date_from,
        'date_to': date_to,
        'payment_method': payment_method
    }

    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Viewed sales report from {date_from} to {date_to} for {payment_method}'
    )
    return render(request, f'system/reports/{payment_method}_sales_report.html', context)

def cash_sales_report(request, date_from, date_to):
    return sales_report_view(request, date_from, date_to, 'cash')

def bank_sales_report(request, date_from, date_to):
    return sales_report_view(request, date_from, date_to, 'bank')

def mobile_sales_report(request, date_from, date_to):
    return sales_report_view(request, date_from, date_to, 'mobile')

@login_required
def awb_details(request, awb_id):
    awb = get_object_or_404(Masterawb, id=awb_id)
    locations = awb.awb_locations.all()
    
    locations_data = []
    for location in locations:
        locations_data.append({
            'rack': location.rack,
            'bay': location.bay,
            'pcs': location.pcs
        })

    ActivityLog.objects.create(
        user=request.user,
        activity_type='READ',
        description=f'Viewed AWB details for MasterAWB ID: {awb.id}, AWB: {awb.awb}'
    )
    return JsonResponse({'locations': locations_data})




@login_required
def activity_log_list(request):
    logs = ActivityLog.objects.all().order_by('timestamp')
    return render(request, 'system/history/activity_log_list.html', {'logs': logs})



@login_required
def trash_view(request):
    trashed_invoices = Invoice.objects.filter(deleted=True)
    trashed_awbs = Masterawb.objects.filter(deleted=True)
    context = {
        'trashed_invoices': trashed_invoices,
        'trashed_awbs': trashed_awbs,
    }
    return render(request, 'system/trash/trash_list.html', context)





@login_required
def restore_invoice(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    awb = invoice.awb
    invoice.deleted = False
    invoice.save()

    if invoice.get_status == 'paid' or invoice.get_status == 'credited':
        awb.bill=False 
        awb.invoice_generated = True
        awb.save()

    ActivityLog.objects.create(
        user=request.user,
        activity_type='UPDATE',
        description=f'Restored Invoice ID: {invoice.id}, Customer: {invoice.customer}'
    )
    messages.success(request, f'Invoice {invoice.customer} restored successfully')
    return redirect('trash')




@login_required
def permanently_delete_invoice(request, id):
    if request.method == 'DELETE' and request.is_ajax():
        try:
            invoice = Invoice.objects.get(pk=id)
            invoice_id = invoice.id
            invoice.delete()

            ActivityLog.objects.create(
                user=request.user,
                activity_type='DELETE',
                description=f'Permanently deleted Invoice ID: {invoice_id}'
            )
            return JsonResponse({'message': 'Invoice permanently deleted.'}, status=200)
        except Invoice.DoesNotExist:
            return JsonResponse({'error': 'Invoice does not exist.'}, status=404)
    return JsonResponse({'error': 'Invalid request.'}, status=400)






@login_required
def restore_awb(request, id):
    awb = get_object_or_404(Masterawb, pk=id)
    awb.deleted = False
    awb.save()

    ActivityLog.objects.create(
        user=request.user,
        activity_type='UPDATE',
        description=f'Restored AWB ID: {awb.awb}'
    )
    messages.success(request, f'AWB {awb.awb} restored successfully')
    return redirect('trash')

@login_required
def permanently_delete_awb(request, id):
    awb = get_object_or_404(Masterawb, pk=id)
    awb_id = awb.id
    awb.delete()

    ActivityLog.objects.create(
        user=request.user,
        activity_type='DELETE',
        description=f'Permanently deleted AWB ID: {awb.awb}'
    )
    messages.success(request, f'AWB {awb.awb} permanently deleted')
    return redirect('trash')








@login_required
def view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'system/users/view_user.html', {'user': user})

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.wharehouse = 'wharehouse' in request.POST
        user.acceptance = 'acceptance' in request.POST
        user.importer = 'importer' in request.POST
        user.accountance = 'accountance' in request.POST
        user.management = 'management' in request.POST
        user.report = 'report' in request.POST
        user.save()
        messages.success(request, 'User updated successfully')
        return redirect(reverse('users'))
    return render(request, 'system/users/edit_user.html', {'user': user})

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully')
    return redirect(reverse('users'))

@login_required
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    new_password = 'new_password'  # Define how you want to generate the new password
    user.set_password(new_password)
    user.save()
    messages.success(request, 'Password reset successfully')
    return redirect(reverse('users'))

@login_required
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, 'User activated successfully')
    return redirect(reverse('users'))

@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, 'User deactivated successfully')
    return redirect(reverse('users'))



@login_required
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect(reverse('users'))
    else:
        form = PasswordResetForm()
    return render(request, 'system/users/reset_password.html', {'form': form, 'user': user})




@login_required
def awb_history(request):
    history = None
    master_awb = None
    awb_number = request.GET.get('awb', None)  # Get AWB from query parameters

    if awb_number:
        master_awb = get_object_or_404(Masterawb, awb=awb_number)
        history = master_awb.history.all().order_by('-changed_at')  # Order by newest first

    # Handle AJAX request for a specific history item
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        history_id = request.GET.get('history_id')
        if history_id:
            history_item = get_object_or_404(AwbHistory, id=history_id)
            return JsonResponse({
                'changed_at': history_item.changed_at.strftime('%Y-%m-%d %H:%M:%S'),
                'changed_by': history_item.changed_by.username if history_item.changed_by else 'Unknown',
                'change_summary': history_item.change_summary,
                'remark': history_item.remark,  # Include remark in the response
            })

    return render(request, 'system/history/awb_history.html', {
        'history': history,
        'master_awb': master_awb,
        'awb_number': awb_number,
    })



class InvoiceHistoryView(ListView):
    model = InvoiceHistory
    template_name = 'system/history/invoice_history.html'
    context_object_name = 'invoice_histories'
    paginate_by = 10
    ordering = ['-performed_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(invoice_id__icontains=search_query) |
                models.Q(awb__icontains=search_query) |
                models.Q(customer__icontains=search_query)
            )
        return queryset





@login_required
def permanently_delete_invoice(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    invoice_id = invoice.id
    
    # Save to invoice history before deleting
    InvoiceHistory.objects.create(
        invoice_id=invoice.id,
        awb=invoice.awb.awb,
        customer=invoice.customer,
        pcs=invoice.awb.awb_pcs,
        weight_kg=invoice.awb.awb_kg,
        origin=invoice.awb.awb_type,
        total_amount_tzs=invoice.total_amount_tzs,
        status=invoice.status,
        action='deleted',
        performed_by=request.user,
        note='Invoice permanently deleted'
    )

    invoice.delete()

    ActivityLog.objects.create(
        user=request.user,
        activity_type='DELETE',
        description=f'Permanently deleted Invoice ID: {invoice_id}'
    )
    messages.success(request, f'Invoice {invoice_id} permanently deleted')
    return redirect('trash')


def edit_invoice_logic(invoice, update_detail_for_invoice, update_status_for_invoices, user):
    # Store the original data in history before editing
    InvoiceHistory.objects.create(
        invoice_id=invoice.id,
        awb=invoice.awb.awb,
        customer=invoice.customer,
        pcs=invoice.awb.awb_pcs,
        weight_kg=invoice.awb.awb_kg,
        origin=invoice.awb.awb_type,
        total_amount_tzs=invoice.total_amount_tzs,
        status=invoice.status,
        action='edited',
        performed_by=user,
        note='Invoice edited'
    )
    
    # Proceed with the edit logic
    invoice.status = update_status_for_invoices
    invoice.invoice_detail = update_detail_for_invoice
    invoice.save()





# FREIGHT MODE
@login_required
def get_freight_by_awb(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        awb_type = request.GET.get('awb_type')
        if awb_type:
            try:
                # Filter Freight records by matching awb_type
                freights = Freight.objects.filter(awb_type=awb_type)
                if freights.exists():
                    freight_data = [{"id": freight.id, "rate": freight.freight_rete} for freight in freights]
                    return JsonResponse({"freights": freight_data})
                else:
                    return JsonResponse({"freights": []})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "awb_type not provided"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)




@login_required
def freight_list(request):
    if not request.user.management:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    freights = Freight.objects.all()
    return render(request, 'system/freight/freight_list.html', {'freights': freights})

@login_required
def rate_list(request):
    if not request.user.management:
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    preferences = SystemPreference.objects.all()
    return render(request, 'system/settings/rate_list.html', {'preferences': preferences})

@login_required
@require_http_methods(["DELETE"])
def delete_freight(request, freight_id):
    if not request.user.management:
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    freight = get_object_or_404(Freight, id=freight_id)

    try:
        # Create a history record before deleting the freight
        FreightHistory.objects.create(
            freight=freight,
            action='deleted',
            performed_by=request.user,
            performed_at=timezone.now()
        )
        freight.delete()
        return JsonResponse({'success': True}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def create_freight(request):
    if not request.user.management:
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    if request.method == 'POST':
        form = FreightForm(request.POST)
        if form.is_valid():
            freight = form.save(commit=False)
            freight.performed_by = request.user  # Set the user who is performing the action
            freight.save()
            return redirect('freight_list')
    else:
        form = FreightForm()
    
    return render(request, 'system/freight/create_freight.html', {'form': form})

@login_required
def update_freight(request, pk):
    if not request.user.management:
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
    freight = get_object_or_404(Freight, pk=pk)
    if request.method == 'POST':
        form = FreightForm(request.POST, instance=freight)
        if form.is_valid():
            freight = form.save(commit=False)
            freight.performed_by = request.user  # Update the user who is performing the action
            freight.save()
            return redirect('freight_list')  # Redirect to the freight list or a success page
    else:
        form = FreightForm(instance=freight)
    
    return render(request, 'system/freight/update_freight.html', {'form': form, 'freight': freight})




# Custom error handlers
def custom_403_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def custom_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

handler403 = custom_403_view
handler404 = custom_404_view
