from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tcra_integration.views import TcraHealthView, TcraSubmissionViewSet, TcraWebhookView

router = DefaultRouter()
router.register("submissions", TcraSubmissionViewSet, basename="tcra-submissions")

urlpatterns = [
    path("api/tcra/", include(router.urls)),
    path("api/tcra/health/", TcraHealthView.as_view(), name="tcra-health"),
    path("webhooks/tcra/", TcraWebhookView.as_view(), name="tcra-webhook"),
]
