from django.shortcuts import render, redirect
from accounts.decorators import authenticated_user
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import PasswordChangingForm, UserForm, SystemForm
from accounts.models import *
from sifex_system.models import *



@authenticated_user
def UserLogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('console')
        else: 
            messages.info(request, 'Username or password is incorrect!')
            return redirect('login')
    context ={}
    return render(request, 'auth/app_login.html', context)



def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required
def settings(request):
    prefrecence = SystemPreference.objects.all()[:1]
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Information updated successfully')
            return redirect('settings')
    context = {
        'form': form,
        'prefrecence': prefrecence,
    }
    return render(request, 'system/settings/account.html', context)


def system_preference(request, pk):
    preference = SystemPreference.objects.get(id=pk)
    form = SystemForm(instance=preference)
    if request.method == 'POST':
        form = SystemForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'preference updated successfully')
            return redirect('preference', preference.id)
    context = {'form': form, 'preference': preference}
    return render(request, 'system/settings/preference.html', context)


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm

    success_url = reverse_lazy('success_password')

@login_required
def success_page(request):
    return render(request, 'system/partials/success_page.html', {})

@login_required
def password_changed_success(request):
    return render(request, 'system/partials/password_success_change.html', {})
