from django.shortcuts import render, redirect
from django.http import JsonResponse
from core.models import *
from sifex_system.models import *



def under_construction(request):
    return render(request, 'home/under_construction.html')

def homepage(request):
    services = Service.objects.all()
    blogs = Post.objects.all()
    teams = Team.objects.all()[:3]
    carousels = Carousel.objects.all()  # Fetch carousel objects
    return render(request, 'home/index.html', {'services': services, 'teams': teams, 'carousels': carousels, 'blogs': blogs})


def services(request):
    services = Service.objects.all()
    return render(request, 'home/services.html', {'services': services})

def about(request):
    teams = Team.objects.all()[:3]
    posts = Post.objects.all()[:5]
    return render(request, 'home/about.html', {'teams': teams, 'posts': posts})

def blog(request):
    posts = Post.objects.all()[:5]
    return render(request, 'home/blog.html', {'posts': posts})


def contact(request):
    return render(request, 'home/contact.html', {})


def Index(request):
    # contacts = Contact.objects.all()
    context = {
        # 'address': contacts,
    }
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_key')
       
        courier_packages = Masterawb.objects.filter(awb=tracking_id)
        courier_parcel = Slaveawb.objects.filter(awb=tracking_id)
        if courier_packages:
            return render(request, 'home/couriers.html', locals())
        if courier_parcel:
            return render(request, 'home/couriers.html', locals())
        else:
            context["errors"] = "Sorry Your tracking id is invalid"
            return render(request, 'home/couriers.html', context)
    else:
        return render(request, 'home/couriers.html', context)



def CourierInfo(request, pk):
    
    # contacts = Contact.objects.all()
    courier = {}
    courier_details = {}
    if courier:
        courier = Slaveawb.objects.get(id = pk)
        courier_details = courier.sub_status.all().order_by('-time')
    else:
        courier = Masterawb.objects.get(id = pk)
        courier_details = courier.master_status.all().order_by('-time')

   
    context = {
        'courier_details': courier_details,
        'courier':courier,
        # 'address': contacts,
    }
    return render(request, 'home/courierInfo.html', context)


# ajax call
def get_posts(request):
    posts = Post.objects.all()
    data = []
    for obj in posts:
        item = {
            'id': obj.pk,
            'title': obj.title,
            'body': obj.body,
        }
        data.append(item)
    return JsonResponse({'data': data})


def load_services(request):
    posts = Post.objects.all()
    data = []
    for obj in posts:
        item = {
            'id': obj.pk,
            'title': obj.title,
            'body': obj.body,
        }
        data.append(item)
    return JsonResponse({'data': data})


def request_a_quote(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        service = request.POST.get('service')
        quote = Quote.objects.create(name=name, email=email, phone=phone, service=service)
        return redirect('home')




def blog_details(request, pk):
    blog = Post.objects.get(id=pk)
    context = {'blog': blog}
    return render(request, 'home/blog_detail.html', context)
