from django.urls import path
from .       import views
from .       import api

app_name = 'camera_management'

urlpatterns = [
    # ── RPi upload (no auth middleware, uses api_key field) ──────────────────
    path('api/upload/', api.receive_detection, name='camera_upload'),

    # ── Supervisor: add a camera via Leaflet map ─────────────────────────────
    path('add/', views.add_camera, name='add_camera'),

    # ── AJAX: fetch cameras for a project (used by Leaflet map) ─────────────
    path('list/', views.list_cameras_for_project, name='list_cameras'),
]
