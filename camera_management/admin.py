from django.contrib import admin
from .models import Camera, Detection


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display  = ('name', 'camera_id', 'project', 'parcelle', 'is_active', 'latitude', 'longitude')
    list_filter   = ('is_active', 'project')
    search_fields = ('name', 'camera_id')
    readonly_fields = ('latitude', 'longitude')


@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display  = ('camera', 'confidence_score', 'detected_at')
    list_filter   = ('camera__project',)
    readonly_fields = ('detected_at', 'bounding_boxes')
