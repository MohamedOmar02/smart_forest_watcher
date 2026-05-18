from django.urls    import path
from .              import  views

urlpatterns = [

    path('client/', views.client_login, name='client_login'),
    path('logout_client/', views.sign_out_client, name='logout_client'),

    path('supervisor/',views.supervisor_login, name = "supervisor_login"),
    path('logout_super/', views.sign_out, name = 'logout_supervisor'),

    # API endpoints for mobile
    path('api/supervisor/login', views.supervisor_api_login, name='supervisor_api_login_no_slash'),
    path('api/supervisor/login/', views.supervisor_api_login, name='supervisor_api_login'),
    path('api/client/login', views.client_api_login, name='client_api_login_no_slash'),
    path('api/client/login/', views.client_api_login, name='client_api_login'),
    path('api/client/register', views.client_api_register, name='client_api_register_no_slash'),
    path('api/client/register/', views.client_api_register, name='client_api_register'),
]