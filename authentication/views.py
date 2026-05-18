import json
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.contrib.auth import login, logout
from client.models import Client
from .forms import ClientLoginForm, SupervisorLoginForm
from supervisor.models.supervisor import Supervisor
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from client.models import Client

logger = logging.getLogger(__name__)

@csrf_exempt
def supervisor_api_login(request):
    response = None
    if request.method == 'OPTIONS':
        response = JsonResponse({})
    elif request.method == 'POST':
        print(f"Received POST: {request.body}")
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            print(f"Parsed data: email={email}, password={password}")
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}")
            response = JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        if response is None:
            if not email or not password:
                response = JsonResponse({'error': 'Email and password required'}, status=400)
            else:
                try:
                    supervisor = Supervisor.objects.get(email=email)
                    valid_login = False
                    if supervisor.user and supervisor.user.check_password(password):
                        valid_login = True
                    elif check_password(password, supervisor.password):
                        valid_login = True

                    if valid_login:
                        login(request, supervisor.user)
                        request.session['supervisor_authenticated'] = True
                        request.session['client_authenticated'] = False
                        response = JsonResponse({
                            'success': True,
                            'message': 'Logged in as supervisor',
                            'user_id': supervisor.user.id,
                            'username': supervisor.user.username,
                            'email': supervisor.email,
                            'role': 'supervisor'
                        })
                    else:
                        response = JsonResponse({'error': 'Invalid credentials'}, status=401)
                except Supervisor.DoesNotExist:
                    response = JsonResponse({'error': 'Supervisor not found'}, status=404)
    else:
        response = JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if response:
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@csrf_exempt
def client_api_login(request):
    response = None
    if request.method == 'OPTIONS':
        response = JsonResponse({})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
        except json.JSONDecodeError:
            response = JsonResponse({'error': 'Invalid JSON'}, status=400)

        if response is None:
            if not email or not password:
                response = JsonResponse({'error': 'Email and password required'}, status=400)
            else:
                try:
                    try:
                        client = Client.objects.get(email=email)
                    except Client.DoesNotExist:
                        client = Client.objects.get(username=email)

                    valid_login = False
                    if client.user and client.user.check_password(password):
                        valid_login = True
                    elif check_password(password, client.password):
                        valid_login = True

                    if valid_login:
                        login(request, client.user)
                        request.session['client_authenticated'] = True
                        request.session['supervisor_authenticated'] = False
                        response = JsonResponse({
                            'success': True,
                            'message': 'Logged in as client',
                            'user_id': client.user.id,
                            'username': client.user.username,
                            'email': client.email,
                            'role': 'client'
                        })
                    else:
                        response = JsonResponse({'error': 'Invalid credentials'}, status=401)
                except Client.DoesNotExist:
                    response = JsonResponse({'error': 'Client not found'}, status=404)
    else:
        response = JsonResponse({'error': 'Method not allowed'}, status=405)

    if response:
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@csrf_exempt
def client_api_register(request):
    response = None
    if request.method == 'OPTIONS':
        response = JsonResponse({})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            response = JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            first_name = data.get('firstName', '').strip()
            last_name = data.get('lastName', '').strip()
            email = data.get('email', '').strip()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            password_confirmation = data.get('password_confirmation', '').strip()
            phone = data.get('phone')

            if not (first_name or last_name):
                response = JsonResponse({'error': 'First name or last name required'}, status=400)
            elif not email or not username or not password or not password_confirmation or not phone:
                response = JsonResponse({'error': 'All fields are required'}, status=400)
            elif password != password_confirmation:
                response = JsonResponse({'error': 'Passwords do not match'}, status=400)
            elif not str(phone).isdigit() or len(str(phone)) != 8:
                response = JsonResponse({'error': 'Phone number must be 8 digits'}, status=400)
            else:
                try:
                    client = Client(
                        firstName=first_name,
                        lastName=last_name,
                        email=email,
                        username=username,
                        password=password,
                        phone=int(phone)
                    )
                    client.save()
                    response = JsonResponse({
                        'success': True,
                        'message': 'Client registered successfully',
                        'user_id': client.user_id,
                        'email': client.email,
                        'username': client.username,
                        'role': 'client'
                    })
                except ValidationError as e:
                    response = JsonResponse({'error': e.message_dict if hasattr(e, 'message_dict') else str(e)}, status=400)
                except Exception as exc:
                    response = JsonResponse({'error': 'Unable to create client account', 'details': str(exc)}, status=500)
    else:
        response = JsonResponse({'error': 'Method not allowed'}, status=405)

    if response:
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@csrf_exempt
def client_login(request):
    get_token(request)
    if request.method == 'POST':
        form_client = ClientLoginForm(request.POST)
        if form_client.is_valid():
            email = form_client.cleaned_data['email']
            password = form_client.cleaned_data['password']
            try:
                client = Client.objects.get(email=email)
                valid_login = False
                if client.user and client.user.check_password(password):
                    valid_login = True
                elif check_password(password, client.password):
                    valid_login = True

                if valid_login:
                    login(request, client.user)
                    request.session['client_authenticated'] = True
                    request.session['supervisor_authenticated'] = False
                    next_url = request.POST.get('next', 'select_project_of_project')
                    return redirect(next_url)
                else:
                    form_client.add_error(None, "Invalid email or password!!!")
            except Client.DoesNotExist:
                form_client.add_error(None, "Invalid email or password!!!")
        return render(request, 'website/client.html', {'form_client': form_client})
    form_client = ClientLoginForm()
    return render(request, 'website/client.html', {'form_client': form_client})


def sign_out_client(request):
    if request.session.get('client_authenticated'):
        request.session.flush()
        logout(request)
    return redirect('client_login')



@csrf_exempt
def supervisor_login(request):
    get_token(request)
    if request.method == 'POST':
        form = SupervisorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                supervisor = Supervisor.objects.get(email=email)
                login(request, supervisor.user)
                request.session['supervisor_authenticated'] = True
                request.session['client_authenticated'] = False
                request.session.modified = True
                next_url = request.POST.get('next', 'supervisor:dashboard_super')
                return redirect(next_url)
            except Supervisor.DoesNotExist:
                form.add_error(None, "Supervisor not found!")
        return render(request, 'website/supervisor.html', {'form': form})
    form = SupervisorLoginForm()
    return render(request, 'website/supervisor.html', {'form': form})




def sign_out(request):
    if request.session.get('supervisor_authenticated'):
        request.session.flush()
        logout(request)
    return redirect('supervisor_login')
