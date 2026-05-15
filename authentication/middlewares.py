# authentication/middlewares.py

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class SimpleCorsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            response['Access-Control-Allow-Credentials'] = 'true'
            return response
        return None

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

class SeparateSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'client'):
                request.session['client_authenticated'] = True
                request.session['supervisor_authenticated'] = False
            elif hasattr(request.user, 'supervisor'):
                request.session['supervisor_authenticated'] = True
                request.session['client_authenticated'] = False
            else:
                request.session.setdefault('client_authenticated', False)
                request.session.setdefault('supervisor_authenticated', False)

    def process_response(self, request, response):
        if request.user.is_authenticated:
            if hasattr(request.user, 'client'):
                request.session['client_authenticated'] = True
            elif hasattr(request.user, 'supervisor'):
                request.session['supervisor_authenticated'] = True
            else:
                request.session.setdefault('client_authenticated', False)
                request.session.setdefault('supervisor_authenticated', False)
        return response
