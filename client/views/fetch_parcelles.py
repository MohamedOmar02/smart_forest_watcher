from django.shortcuts                   import get_object_or_404
from django.contrib.auth.decorators     import login_required
from django.http                        import JsonResponse
from authentication.decorators          import client_required
from supervisor.models.data             import Data
from supervisor.models.project          import Project
from supervisor.models.parcelle         import Parcelle
from supervisor.models.node             import Node
from camera_management.models          import Camera



@login_required(login_url='client_login')
@client_required
def fetch_parcelles_for_project(request):
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'No project ID provided.'}, status=400)

    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    parcelles = Parcelle.objects.filter(project=project)
    parcelle_data = []
    all_nodes = []

    for parcelle in parcelles:
        nodes = Node.objects.filter(parcelle=parcelle)
        node_data = [{
            'id': node.id,
            'name': node.name,
            'latitude': node.position.x,  
            'longitude': node.position.y, 
            'ref': node.reference, 
            'last_data': get_last_data(node)
        } for node in nodes]
        
        all_nodes.extend(node_data)

        parcelle_data.append({
            'id': parcelle.id,
            'name': parcelle.name,
            'coordinates': list(parcelle.polygon.coords[0]),
            'nodes': node_data
        })

    city_data = {
        'localite_libelle': project.city.localite_libelle,
        'latitude': project.city.latitude,
        'longitude': project.city.longitude
    }
    
    # Fetch Cameras for the project
    cameras = Camera.objects.filter(project=project)
    camera_data = []
    for c in cameras:
        has_alert = False
        try:
            # Check if camera has a linked FireDetection (One-to-One)
            if hasattr(c, 'detection'):
                has_alert = True
        except Exception:
            pass
            
        latest_detection = c.detections.order_by('-detected_at').first()
        image_url = None
        if latest_detection and latest_detection.image:
            try:
                image_url = latest_detection.image.url
            except ValueError:
                pass
                
        camera_data.append({
            'id': c.id,
            'name': c.name,
            'camera_id': c.camera_id,
            'latitude': float(c.latitude) if c.latitude else c.position.y if c.position else 0,
            'longitude': float(c.longitude) if c.longitude else c.position.x if c.position else 0,
            'has_alert': has_alert or (latest_detection is not None),
            'is_active': c.is_active,
            'latest_alert_image': image_url,
            'latest_alert_time': latest_detection.detected_at.strftime('%Y-%m-%d %H:%M:%S') if latest_detection else None
        })
    

    return JsonResponse({
        'parcelles': parcelle_data,
        'city': city_data,
        'cameras': camera_data,
    })


def get_last_data(node):
    try:
        last_data = Data.objects.filter(node=node).latest('published_date')
        return {
            'temperature': last_data.temperature,
            'humidity': last_data.humidity,
            'rssi': node.RSSI,
            'fwi': node.FWI,
            'prediction_result': node.detection,
            'pressure': last_data.pressur,
            'gaz': last_data.gaz,
            'wind_speed': last_data.wind,
            'rain_volume': last_data.rain,
        }
    except Data.DoesNotExist:
        return {}
    
#تعمل API
# ترجع JSON
# frontend يستعملها باش يرسم map 

# يرسم parcelles (polygon)
#يحط nodes (markers)
#يعرض data   