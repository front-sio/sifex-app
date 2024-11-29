from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.http import HttpResponsePermanentRedirect

def redirect_to_root(request):
    return HttpResponsePermanentRedirect("https://sifex.co.tz")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('sifex/', include('sifex_system.urls')),
    path('accounts/', include('accounts.urls')),
    path("www/", redirect_to_root),
]

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



