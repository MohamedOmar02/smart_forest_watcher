import logging
from django.shortcuts               import render, redirect
from django.contrib.auth            import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms                         import ClientLoginForm, SupervisorLoginForm
from django.contrib.auth.hashers    import check_password

try:
    from client.models import Client
except Exception:
    Client = None

try:
    from supervisor.models.supervisor import Supervisor
except Exception:
    Supervisor = None

logger = logging.getLogger(__name__)
User = get_user_model()


def _login_user_by_email(email, password, role):
    if role == 'client' and Client is not None:
        try:
            client = Client.objects.get(email=email)
            if check_password(password, client.password):
                return client.user
        except Client.DoesNotExist:
            pass

    if role == 'supervisor' and Supervisor is not None:
        try:
            supervisor = Supervisor.objects.get(email=email)
            if check_password(password, supervisor.password):
                return supervisor.user
        except Supervisor.DoesNotExist:
            pass

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if user.check_password(password):
        return user
    return None

def client_login(request):
    if request.user.is_authenticated:
        return redirect('notifications')

    if request.method == 'POST':
        form_client = ClientLoginForm(request.POST)
        if form_client.is_valid():
            email = form_client.cleaned_data['email']
            password = form_client.cleaned_data['password']
            user = _login_user_by_email(email, password, 'client')
            if user is not None:
                login(request, user)
                request.session['client_authenticated'] = True
                request.session['supervisor_authenticated'] = False
                next_url = request.POST.get('next', 'notifications')
                return redirect(next_url)
            else:
                form_client.add_error(None, "Invalid email or password!!!")
        return render(request, 'website/client.html', {'form_client': form_client})
    form_client = ClientLoginForm()
    return render(request, 'website/client.html', {'form_client': form_client})


def sign_out_client(request):
    if request.session.get('client_authenticated'):
        request.session.flush()
        logout(request)
    return redirect('client_login')



def supervisor_login(request):
    if request.user.is_authenticated:
        return redirect('notifications')

    if request.method == 'POST':
        form = SupervisorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = _login_user_by_email(email, password, 'supervisor')
            if user is not None:
                login(request, user)
                request.session['supervisor_authenticated'] = True
                request.session['client_authenticated'] = False
                next_url = request.POST.get('next', 'notifications')
                return redirect(next_url)
            form.add_error(None, "Invalid email or password!!!")
        return render(request, 'website/supervisor.html', {'form': form})
    form = SupervisorLoginForm()
    return render(request, 'website/supervisor.html', {'form': form})




def sign_out(request):
    if request.session.get('supervisor_authenticated'):
        request.session.flush()
        logout(request)
    return redirect('supervisor_login')


@login_required(login_url='client_login')
def notifications(request):
    return render(request, 'website/notifications.html')
