# from django.shortcuts import redirect
# from django.urls import reverse

# class UnderConstructionMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Define the path for the under construction page
#         under_construction_path = reverse('under_construction')

#         # Allow access to the admin interface and the under construction page itself
#         if not request.path.startswith('/admin/') and request.path != under_construction_path:
#             return redirect('under_construction')
        
#         response = self.get_response(request)
#         return response
