# authentication/middlewares.py

from django.utils.deprecation import MiddlewareMixin

class SeparateSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'client'):
                request.session['client_authenticated'] = True
                request.session['supervisor_authenticated'] = False
            elif hasattr(request.user, 'supervisor'):
                request.session['supervisor_authenticated'] = True
                request.session['client_authenticated'] = False

    def process_response(self, request, response):
        if request.user.is_authenticated:
            if hasattr(request.user, 'client'):
                request.session['client_authenticated'] = True
            elif hasattr(request.user, 'supervisor'):
                request.session['supervisor_authenticated'] = True
        return response
