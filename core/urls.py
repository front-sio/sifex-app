from django.urls import path
from .views import *

urlpatterns = [
    # path('under_construction/', under_construction, name='under_construction'),
    path('', homepage, name="home"),
    path('about/', about, name="about"),
    path('services/', services, name="services"),
    path('blog/', blog, name="blog"),
    path('contact/', contact, name="contact"),
    path('courier/', Index, name="courier"),
    path('courier/<str:pk>/courier_detail', CourierInfo, name="courier_detail"),

    path('get_services/', load_services, name="load_services"),
    path('get_posts/', get_posts, name="get_posts"),
    path('request_quote/', request_a_quote, name="request_quote"),

    path('blog_detail/<int:pk>', blog_details, name='blog_detail'),
]
