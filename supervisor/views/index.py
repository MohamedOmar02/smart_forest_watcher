from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from authentication.decorators      import supervisor_required
from django.http                    import JsonResponse
from supervisor.models.project      import Project
from supervisor.models.parcelle     import Parcelle
from supervisor.models.node         import Node
from supervisor.models.data         import Data
from camera_management.models       import Camera

@login_required(login_url='supervisor_login')
@supervisor_required
def index(request):
    total_nodes = Node.objects.count()
    total_cameras = Camera.objects.count()
    total_projects = Project.objects.count()
    
    context = {
        'total_nodes': total_nodes,
        'total_cameras': total_cameras,
        'total_projects': total_projects,
    }
    return render(request, 'website/index.html', context)

@login_required(login_url='supervisor_login')
@supervisor_required
def get_all_assets(request):
    projects = Project.objects.all()
    data = []
    
    for project in projects:
        parcelles_data = []
        parcelles = Parcelle.objects.filter(project=project)
        for parcelle in parcelles:
            nodes = Node.objects.filter(parcelle=parcelle)
            node_data = [{
                'id': node.id,
                'name': node.name,
                'latitude': float(node.latitude) if node.latitude else (node.position.y if node.position else None),
                'longitude': float(node.longitude) if node.longitude else (node.position.x if node.position else None),
                'ref': node.reference,
                'last_data': get_last_data(node)
            } for node in nodes]

            cameras = Camera.objects.filter(parcelle=parcelle)
            camera_data = []
            for cam in cameras:
                latest_detection = cam.detections.order_by('-detected_at').first()
                image_url = None
                if latest_detection and latest_detection.image:
                    try:
                        image_url = latest_detection.image.url
                    except ValueError:
                        pass
                
                camera_data.append({
                    'id': cam.id,
                    'name': cam.name,
                    'camera_id': cam.camera_id,
                    'is_active': cam.is_active,
                    'latitude': float(cam.latitude) if cam.latitude else None,
                    'longitude': float(cam.longitude) if cam.longitude else None,
                    'has_alert': hasattr(cam, 'detection') or (latest_detection is not None),
                    'latest_alert_image': image_url,
                    'latest_alert_time': latest_detection.detected_at.strftime('%Y-%m-%d %H:%M:%S') if latest_detection else None
                })

            parcelles_data.append({
                'id': parcelle.id,
                'name': parcelle.name,
                'coordinates': list(parcelle.polygon.coords[0]) if parcelle.polygon else [],
                'nodes': node_data,
                'cameras': camera_data
            })
            
        data.append({
            'project_id': project.pk,
            'project_name': project.name,
            'parcelles': parcelles_data
        })
        
    return JsonResponse({'projects': data}, status=200)

def get_last_data(node):
    try:
        last_data = Data.objects.filter(node=node).latest('published_date')
        return {
            'temperature': last_data.temperature,
            'humidity': last_data.humidity,
            'rssi': node.RSSI,
            'fwi': node.FWI,
            'fwi_predit': getattr(last_data, 'fwi_predit', 0),
            'prediction_result': node.detection,
            'pressure': last_data.pressur,
            'gaz': last_data.gaz,
            'wind_speed': getattr(last_data, 'wind', None),
            'rain_volume': getattr(last_data, 'rain', None),
        }
    except Data.DoesNotExist:
        return {}