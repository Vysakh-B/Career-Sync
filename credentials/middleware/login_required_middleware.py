# from django.shortcuts import redirect
# from django.urls import reverse
# from django.utils.deprecation import MiddlewareMixin

# # Paths that should NOT require login (public paths)
# EXEMPT_PATHS = [
#     '/signin/',
#     '',
#     '/signup/',
#     '/faq/',
#     '/logout/',
#     '/about/',
#     '/privacy/',
#     '/terms/',
#     '/contact/',
# ]

# class LoginRequiredMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         path = request.path_info

#         if not request.user.is_authenticated:
#             if not any(path.startswith(exempt) for exempt in EXEMPT_PATHS):
#                 return redirect(reverse('signin'))

#     def process_response(self, request, response):
#         # Prevent browser caching
#         response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#         response['Pragma'] = 'no-cache'
#         response['Expires'] = '0'
#         return response