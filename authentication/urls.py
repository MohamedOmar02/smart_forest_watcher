from django.urls import path
from . import views, api

urlpatterns = [
    path('client/', views.client_login, name='client_login'),
    path('logout_client/', views.sign_out_client, name='logout_client'),

    path('supervisor/', views.supervisor_login, name='supervisor_login'),
    path('logout_super/', views.sign_out, name='logout_supervisor'),
    path('notifications/', views.notifications, name='notifications'),

    # Mobile API
    path('api/login/', api.login, name='api_login'),
    path('api/notifications/', api.notifications, name='api_notifications'),
]