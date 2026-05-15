import json

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import ApiToken

try:
    from client.models import Client
except Exception:
    Client = None

try:
    from supervisor.models.supervisor import Supervisor
except Exception:
    Supervisor = None


User = get_user_model()


def _parse_json_request(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _get_authorization_token(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Token '):
        return auth_header[6:].strip()
    return None


def _token_required(view_func):
    def wrapper(request, *args, **kwargs):
        token = _get_authorization_token(request)
        if not token:
            return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
        try:
            api_token = ApiToken.objects.select_related('user').get(key=token)
        except ApiToken.DoesNotExist:
            return JsonResponse({'detail': 'Invalid token.'}, status=401)
        request.user = api_token.user
        return view_func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'POST only.'}, status=405)

    payload = _parse_json_request(request)
    if payload is None:
        return JsonResponse({'detail': 'Invalid JSON payload.'}, status=400)

    email = payload.get('email', '').strip()
    password = payload.get('password', '').strip()
    if not email or not password:
        return JsonResponse({'detail': 'Email and password are required.'}, status=400)

    user = None
    role = None

    if Client is not None:
        try:
            client = Client.objects.get(email=email)
            if check_password(password, client.password):
                user = client.user
                role = 'client'
        except Client.DoesNotExist:
            pass

    if not user and Supervisor is not None:
        try:
            supervisor = Supervisor.objects.get(email=email)
            if check_password(password, supervisor.password):
                user = supervisor.user
                role = 'supervisor'
        except Supervisor.DoesNotExist:
            pass

    if not user:
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                role = 'user'
            else:
                user = None
        except User.DoesNotExist:
            pass

    if not user:
        return JsonResponse({'detail': 'Invalid email or password.'}, status=401)

    api_token = ApiToken.objects.create(user=user)
    return JsonResponse({'token': api_token.key, 'role': role, 'email': email})


@_token_required
def notifications(request):
    return JsonResponse({'notifications': []}, status=200)
