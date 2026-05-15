from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

try:
    from client.models import Client
except Exception:
    Client = None

try:
    from supervisor.models.supervisor import Supervisor
except Exception:
    Supervisor = None


User = get_user_model()


def _get_user_by_email(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

class SupervisorLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': 'email',
                'name': 'email',
                'placeholder': 'Email',
                'class': 'login__input'
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'id': 'password',
                'name': 'password',
                'placeholder': 'Password',
                'class': 'login__input'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            if Supervisor is not None:
                try:
                    supervisor = Supervisor.objects.get(email=email)
                except Supervisor.DoesNotExist:
                    supervisor = None
                if supervisor is not None:
                    if not check_password(password, supervisor.password):
                        raise forms.ValidationError("Invalid email or password!!!")
                    return cleaned_data

            user = _get_user_by_email(email)
            if user is None or not user.check_password(password):
                raise forms.ValidationError("Invalid email or password!!!")
        
        return cleaned_data


class ClientLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': 'email',
                'name': 'email',
                'placeholder': 'Email',
                'class': 'login__input'
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'id': 'password',
                'name': 'password',
                'placeholder': 'Password',
                'class': 'login__input'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            if Client is not None:
                try:
                    client = Client.objects.get(email=email)
                except Client.DoesNotExist:
                    client = None
                if client is not None:
                    if not check_password(password, client.password):
                        raise forms.ValidationError("Invalid email or password!!!")
                    return cleaned_data

            user = _get_user_by_email(email)
            if user is None or not user.check_password(password):
                raise forms.ValidationError("Invalid email or password!!!")
        
        return cleaned_data
