from django.http import HttpResponse
from django.shortcuts import redirect


def authenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('console')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func



def allowed_user(allowed_role=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_vendor:
                wrapper_func(request, *args, **kwargs)
            elif request.user.is_office:
                wrapper_func(request, *args, **kwargs)
            elif request.user.is_reception:
                wrapper_func(request, *args, **kwargs)
            else:
                return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator




def acceptance(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.management and request.user.is_active:
            return redirect('reception_console')
        elif request.user.delivery_man and request.user.is_active:
            return redirect('console')
        elif request.user.importer and request.user.is_active:
            return redirect('office_console')
        elif request.user.acceptance and request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper_func



def delivery(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.management and request.user.is_active:
            return redirect('reception_console')
        elif request.user.acceptance and request.user.is_active:
            return redirect('console')
        elif request.user.importer and request.user.is_active:
            return redirect('office_console')
        elif request.user.delivery_man and request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper_func


def management(view_func):
    def wrapper_func(request, *args, **kwargs):
        # if request.user.management and request.user.is_active:
        #     return redirect('reception_console')
        if request.user.acceptance and request.user.is_active:
            return redirect('console')
        elif request.user.importer and request.user.is_active:
            return redirect('office_console')
        elif request.user.delivery_man and request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper_func