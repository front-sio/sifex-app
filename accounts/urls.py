from django.urls import path
from accounts.views import *

urlpatterns = [
# accounts and authentications
path('login/',  UserLogin, name="login"),
path('logout/',  logoutUser, name="logout"),
path('success/', success_page, name="success_page"),
path('settings/', settings, name="settings"),
path('preference/<int:pk>/', system_preference, name="preference"),
path('password_changed_success/', password_changed_success, name="success_password"),
path('password-change/', PasswordsChangeView.as_view(template_name="system/partials/password_change.html"), name="change_password"),
]