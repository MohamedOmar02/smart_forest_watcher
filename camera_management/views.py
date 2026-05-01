"""
Views for camera_management.

add_camera  — supervisor places a camera on the Leaflet map (same UX as add_node).
              POST → validates point is inside parcelle → saves Camera → returns JSON.
              GET  → returns the camera form (rendered inline in project.html).

list_cameras_for_project — AJAX endpoint: returns all cameras for a project_id.
                           Used by the map to render camera markers alongside nodes.
"""

import json
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos        import Point
from django.http                    import JsonResponse
from django.shortcuts               import get_object_or_404, render
from authentication.decorators      import supervisor_required, client_required
from supervisor.models.parcelle     import Parcelle
from supervisor.models.project      import Project
from .models  import Camera
from .forms   import CameraForm


@login_required(login_url='supervisor_login')
@supervisor_required
def add_camera(request):
    if request.method == 'POST':
        camera_form = CameraForm(request.POST)

        if camera_form.is_valid():
            coordinates_data = request.POST.get('position', '')
            parcelle_id      = request.POST.get('parcelle')

            try:
                # Parse "POINT(lng lat)" — same parsing as node_create
                coords    = coordinates_data.strip('POINT()').split()
                longitude = float(coords[0])
                latitude  = float(coords[1])
                point     = Point(latitude, longitude)

                parcelle = get_object_or_404(Parcelle, id=parcelle_id)

                if not parcelle.polygon.contains(point):
                    return JsonResponse(
                        {'error': {'_all__': 'The camera must be placed inside the parcelle.'}},
                        status=400
                    )

                camera           = camera_form.save(commit=False)
                camera.position  = point
                camera.latitude  = latitude
                camera.longitude = longitude
                camera.parcelle  = parcelle
                camera.project   = parcelle.project
                camera.save()

                # Return all cameras for this parcelle so the map updates
                cameras = [
                    {
                        'id':        c.id,
                        'name':      c.name,
                        'camera_id': c.camera_id,
                        'latitude':  float(c.latitude),
                        'longitude': float(c.longitude),
                        'has_alert': c.detections.exists(),
                    }
                    for c in Camera.objects.filter(parcelle=parcelle)
                ]

                return JsonResponse({
                    'message':     'Camera added successfully.',
                    'cameras':     cameras,
                    'parcelle_id': parcelle.id,
                    'project_id':  parcelle.project.polygon_id,
                }, status=200)

            except (ValueError, TypeError):
                return JsonResponse(
                    {'error': {'coordinates': [{'message': 'Invalid coordinates.', 'code': 'invalid'}]}},
                    status=400
                )
        else:
            return JsonResponse({'error': camera_form.errors.get_json_data()}, status=400)

    else:
        camera_form = CameraForm()
        return render(request, 'website/project.html', {'camera_form': camera_form})


@login_required(login_url='supervisor_login')
@supervisor_required
def list_cameras_for_project(request):
    """AJAX: return cameras + their alert status for a given project_id."""
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'No project_id provided'}, status=400)

    cameras = Camera.objects.filter(
        project_id=project_id
    ).select_related('parcelle').prefetch_related('detections')

    data = []
    for c in cameras:
        try:
            det         = c.detections.latest('detected_at')
            has_alert   = True
            detected_at = det.detected_at.isoformat()
            image_url   = det.image.url
            confidence  = det.confidence_score
        except Exception:
            has_alert   = False
            detected_at = None
            image_url   = None
            confidence  = None

        data.append({
            'id':          c.id,
            'name':        c.name,
            'camera_id':   c.camera_id,
            'parcelle_id': c.parcelle_id,
            'latitude':    float(c.latitude)  if c.latitude  else None,
            'longitude':   float(c.longitude) if c.longitude else None,
            'is_active':   c.is_active,
            'has_alert':   has_alert,
            'detected_at': detected_at,
            'image_url':   image_url,
            'confidence':  confidence,
        })

    return JsonResponse({'cameras': data}, status=200)

@login_required(login_url='client_login')
@client_required
def camera_detail(request, project_id, camera_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    camera = get_object_or_404(Camera, id=camera_id, project=project)

    # All detections ordered newest first
    all_detections = camera.detections.order_by('-detected_at')
    latest    = all_detections.first()          # shown prominently at top
    history   = all_detections[1:6]             # previous 5 detections shown below

    context = {
        'project':   project,
        'camera':    camera,
        'detection': latest,     # keeps template variable name compatible
        'history':   history,
    }

    return render(request, 'camera_management/camera_detail.html', context)

@login_required(login_url='client_login')
@client_required
def delete_detection(request, detection_id):
    if request.method == 'POST':
        from .models import Detection
        detection = get_object_or_404(Detection, id=detection_id)
        
        # Ensure client owns the project
        if detection.camera.project.client != request.user.client:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        detection.delete()
        return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
