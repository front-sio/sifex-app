from django.http import HttpResponsePermanentRedirect

class RedirectToWWWMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        # Redirect only if the hostname is exactly sifex.co.tz
        if host == "sifex.co.tz":
            return HttpResponsePermanentRedirect(f"https://www.sifex.co.tz{request.get_full_path()}")
        return self.get_response(request)
