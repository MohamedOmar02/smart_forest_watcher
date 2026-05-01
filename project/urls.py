from django.contrib import admin
from django.urls    import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',              admin.site.urls),
    path('',                    include('home.urls')),
    path('connect_as/',         include('authentication.urls')),
    path('dashboard_super/',    include('supervisor.urls')),
    path('dashboard_client/',   include('client.urls')),
    path('camera_management/',  include('camera_management.urls')),
    path('i18n/',               include('django.conf.urls.i18n')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

