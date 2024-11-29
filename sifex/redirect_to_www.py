from django.http import HttpResponsePermanentRedirect

class RedirectToWWWMiddleware:
    """
    Middleware to redirect non-www requests (e.g., sifex.co.tz) to www (e.g., www.sifex.co.tz).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        # Redirect only if the host is non-www
        if host == "sifex.co.tz":
            return HttpResponsePermanentRedirect(f"https://www.sifex.co.tz{request.get_full_path()}")
        return self.get_response(request)
